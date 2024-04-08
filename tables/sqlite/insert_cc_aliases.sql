/* Create CC Aliases */
.param set :extra_content_source 'Adv Content'
INSERT INTO alias SELECT 'ChitChat', json_each.value, :extra_content_source FROM json_each('[
	"Chit Chat"
]');

INSERT INTO alias SELECT 'Radical Spin', json_each.value, :extra_content_source FROM json_each('[
	"RadicalSpin"
]');

INSERT INTO alias SELECT 'Skateboard Dog', json_each.value, :extra_content_source FROM json_each('[
	"SkateboardDog"
]');


INSERT INTO alias SELECT 'Night Drifters', json_each.value, :extra_content_source FROM json_each('[
	"NightDrifters"
]');

INSERT INTO alias SELECT 'Underground Broadcast', json_each.value, :extra_content_source FROM json_each('[
	"UndergroundBroadcast"
]');


INSERT INTO alias SELECT 'Mystic Lilies', json_each.value, :extra_content_source FROM json_each('[
	"MysticLilies"
]');

INSERT INTO alias SELECT 'Genso Network', json_each.value, :extra_content_source FROM json_each('[
	"GensoNetwork",
	"Genso"
]');

INSERT INTO alias SELECT 'Leximancy', json_each.value, :extra_content_source FROM json_each('[
	""
]');


INSERT INTO alias SELECT 'New Connections', json_each.value, :extra_content_source FROM json_each('[
	"NewConnections"
]');

INSERT INTO alias SELECT 'Silicon Skin', json_each.value, :extra_content_source FROM json_each('[
	"SiliconSkin"
]');


INSERT INTO alias SELECT 'The Walls Will Swallow You', json_each.value, :extra_content_source FROM json_each('[
	"TWWSY",
	"TheWallsWillSwallowYou",
	"The Walls",
	"TheWalls",
	"Walls"
]');


INSERT INTO alias SELECT 'MUDSLURP', json_each.value, :extra_content_source FROM json_each('[
	"MUD"
]');


INSERT INTO alias SELECT 'Tarot', json_each.value, :extra_content_source FROM json_each('[
	""
]');


INSERT INTO alias SELECT 'Summer Camp', json_each.value, :extra_content_source FROM json_each('[
	"Summber Camp",
	"SummerCamp",
	"Summer",
	"Sunmer Camp"
]');


INSERT INTO alias SELECT 'Nyx', json_each.value, :extra_content_source FROM json_each('[
	""
]');

INSERT INTO alias SELECT 'Cast the Dice', json_each.value, :extra_content_source FROM json_each('[
	"CasttheDice",
	"CastDice",
	"Cast Dice"
]');

INSERT INTO alias SELECT 'Neko Virus', json_each.value, :extra_content_source FROM json_each('[
	"Neko Virus Infection",
	"NekoVirus"
]');
