// A second player for tools/playtest.py, who fishes. The Minecraft (Java) MCP server's bot has no tool for using an
// item, so casting and reeling in are done by this plain mineflayer client, using the mineflayer that MCP server
// installed (its path in MINEFLAYER). It joins as Fisher and reads one command a line from stdin:
//   look <x> <y> <z>   face a point        cast   use the rod (cast)        reel   use it again (reel in)        quit
// and answers each with a line starting "ok" or "error".

const mineflayer = require(process.env.MINEFLAYER || "mineflayer");
const readline = require("readline");
const path = require("path");
const { Vec3 } = require(process.env.MINEFLAYER ? path.join(process.env.MINEFLAYER, "..", "vec3") : "vec3");

const bot = mineflayer.createBot({ host: process.env.HOST || "localhost", port: Number(process.env.PORT || 25565), username: "Fisher" });
const say = (line) => process.stdout.write(line + "\n");

bot.once("spawn", () => {
	say("ok spawned");
	readline.createInterface({ input: process.stdin }).on("line", async (line) => {
		const [verb, ...args] = line.trim().split(/\s+/);
		try {
			if (verb === "look") {
				const [x, y, z] = args.map(Number);
				await bot.lookAt(new Vec3(x, y, z), true);
			} else if (verb === "cast" || verb === "reel") {
				const rod = bot.inventory.items().find((item) => item.name === "fishing_rod");
				if (!rod) throw new Error("no fishing rod");
				await bot.equip(rod, "hand");
				bot.activateItem();
			} else if (verb === "quit") {
				bot.quit();
				say("ok bye");
				process.exit(0);
			}
			say(`ok ${verb}`);
		} catch (error) {
			say(`error ${error.message}`);
		}
	});
});
bot.on("kicked", (reason) => say(`error kicked ${JSON.stringify(reason)}`));
bot.on("error", (error) => say(`error ${error.message}`));
