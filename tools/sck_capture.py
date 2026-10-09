"""Records one take of the Minecraft client on a Mac: its picture and its own sound, together, into one .mp4.

The trailer skill's capture.py records with Windows' Desktop Duplication and a WASAPI loopback; a Mac has neither,
and no loopback device without installing one. ScreenCaptureKit gives both: a stream filtered to the Minecraft
client's application captures only that app's picture and only its sound (no notification or other app can leak in),
and SCRecordingOutput (macOS 15 and later) writes them to one file, in step.

    python tools/sck_capture.py <out.mp4> <seconds> [--scale 0.75] [--app java]

The take is the whole display the game is on, so run the game fullscreen. --scale sets the recorded size against the
display's pixels (a 3456x2234 display at 0.75 records 2592x1676, enough for a 1920x1080 crop). It needs the Screen
Recording permission for the app it runs under. Needs pyobjc-framework-ScreenCaptureKit and -AVFoundation.
"""

import argparse
import sys
import time

import AVFoundation
import objc
import Foundation
import ScreenCaptureKit as SCK
from Foundation import NSObject


def pump(seconds: float) -> None:
    Foundation.NSRunLoop.currentRunLoop().runUntilDate_(Foundation.NSDate.dateWithTimeIntervalSinceNow_(seconds))


def wait(box: dict, key: str, timeout: float = 15.0) -> None:
    end = time.time() + timeout
    while key not in box and time.time() < end:
        pump(0.05)
    if key not in box:
        sys.exit(f"timed out waiting for {key}")


class RecordingDelegate(NSObject):
    def init(self):
        self = objc.super(RecordingDelegate, self).init()
        self.box = {}
        return self

    def recordingOutputDidStartRecording_(self, output):
        self.box["started"] = time.time()

    def recordingOutput_didFailWithError_(self, output, error):
        self.box["error"] = str(error)

    def recordingOutputDidFinishRecording_(self, output):
        self.box["finished"] = time.time()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("out")
    parser.add_argument("seconds", type=float)
    parser.add_argument("--scale", type=float, default=0.75)
    parser.add_argument("--app", default="java", help="the recorded application's name (the Java client runs as java)")
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args()

    box: dict = {}

    def got_content(content, error):
        box["content"], box["content_error"] = content, error

    SCK.SCShareableContent.getShareableContentExcludingDesktopWindows_onScreenWindowsOnly_completionHandler_(True, True, got_content)
    wait(box, "content")
    content = box["content"]
    if content is None:
        sys.exit(f"no shareable content: {box['content_error']}")
    apps = [a for a in content.applications() if (a.applicationName() or "").lower() == args.app.lower()]
    windows = [w for w in content.windows() if w.owningApplication() and (w.owningApplication().applicationName() or "").lower() == args.app.lower()]
    if not apps or not windows:
        sys.exit(f"no running application named {args.app} with a window on screen")
    # The display the game's window is on.
    frame = windows[0].frame()
    display = next((d for d in content.displays() if Foundation.NSPointInRect(frame.origin, d.frame())), content.displays()[0])
    content_filter = SCK.SCContentFilter.alloc().initWithDisplay_includingApplications_exceptingWindows_(display, apps, [])

    config = SCK.SCStreamConfiguration.alloc().init()
    scale = content_filter.pointPixelScale() * args.scale
    width, height = int(display.width() * scale) // 2 * 2, int(display.height() * scale) // 2 * 2
    config.setWidth_(width)
    config.setHeight_(height)
    config.setMinimumFrameInterval_(AVFoundation.CMTimeMake(1, args.fps))
    config.setShowsCursor_(False)
    config.setCapturesAudio_(True)
    config.setSampleRate_(48000)
    config.setChannelCount_(2)
    config.setExcludesCurrentProcessAudio_(True)

    recording_config = SCK.SCRecordingOutputConfiguration.alloc().init()
    recording_config.setOutputURL_(Foundation.NSURL.fileURLWithPath_(args.out))
    recording_config.setOutputFileType_(AVFoundation.AVFileTypeMPEG4)
    recording_config.setVideoCodecType_(AVFoundation.AVVideoCodecTypeH264)
    delegate = RecordingDelegate.alloc().init()
    recording = SCK.SCRecordingOutput.alloc().initWithConfiguration_delegate_(recording_config, delegate)

    stream = SCK.SCStream.alloc().initWithFilter_configuration_delegate_(content_filter, config, None)
    ok, error = stream.addRecordingOutput_error_(recording, None)
    if not ok:
        sys.exit(f"could not add the recording output: {error}")

    def started(error):
        box["capture_started"] = error

    stream.startCaptureWithCompletionHandler_(started)
    wait(box, "capture_started")
    if box["capture_started"] is not None:
        sys.exit(f"could not start capturing: {box['capture_started']}")
    begin = time.time()
    while time.time() - begin < args.seconds and "error" not in delegate.box:
        pump(0.1)

    def stopped(error):
        box["capture_stopped"] = error

    stream.stopCaptureWithCompletionHandler_(stopped)
    wait(box, "capture_stopped")
    end = time.time() + 15
    while "finished" not in delegate.box and "error" not in delegate.box and time.time() < end:
        pump(0.1)
    if "error" in delegate.box:
        sys.exit(f"recording failed: {delegate.box['error']}")
    print(f"wrote {args.out} ({width}x{height}, {time.time() - begin:.1f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
