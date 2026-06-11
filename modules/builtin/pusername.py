from core.base_module import Module
import aiohttp
import asyncio
import random


class PUsernameModule(Module):
    NAME = 'Username Finder'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Поиск свободных 5-символьных юзернеймов из английского словаря'
    DEPENDENCIES = ['aiohttp']
    COMMANDS = {
        'pusername': 'Найти свободные юзернеймы (например: .pusername 5)',
    }

    async def init(self, client, command_prefix, events, load_module,
                   loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.words_cache = None
        self.WORDS_URLS = [
            'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt',
            'https://raw.githubusercontent.com/Roman-/dicts/master/research/eng_all_86k.txt',
            'https://raw.githubusercontent.com/ileygb8cwqogn8c/different_lists/master/%D0%90%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9%20%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D1%8C%20%27English%27%20%20318971%20%203%2C44%20%D0%9C%D0%91.txt',
        ]
        self.BUILTIN_WORDS = [
            'about', 'above', 'abuse', 'actor', 'acute', 'admit', 'adopt', 'adult', 'after', 'again',
            'agent', 'agree', 'ahead', 'alarm', 'album', 'alert', 'alike', 'alive', 'allow', 'alone',
            'along', 'alter', 'amber', 'among', 'angel', 'anger', 'angle', 'angry', 'apart', 'apple',
            'apply', 'arena', 'argue', 'arise', 'armed', 'arrow', 'aside', 'asset', 'audio', 'audit',
            'avoid', 'award', 'aware', 'badly', 'baker', 'bases', 'basic', 'beach', 'began', 'begin',
            'begun', 'being', 'below', 'bench', 'birth', 'black', 'blame', 'blind', 'block', 'blood',
            'board', 'boost', 'booth', 'bound', 'brain', 'brand', 'brave', 'bread', 'break', 'brick',
            'brief', 'bring', 'broad', 'broke', 'brown', 'build', 'built', 'buyer', 'cable', 'carry',
            'catch', 'cause', 'chain', 'chair', 'chart', 'chase', 'cheap', 'check', 'chest', 'chief',
            'child', 'china', 'chose', 'civil', 'claim', 'class', 'clean', 'clear', 'clerk', 'click',
            'clock', 'close', 'coach', 'coast', 'could', 'count', 'court', 'cover', 'craft', 'crash',
            'cream', 'crime', 'cross', 'crowd', 'crown', 'curve', 'cycle', 'daily', 'dance', 'dated',
            'dealt', 'death', 'debut', 'delay', 'depth', 'doing', 'doubt', 'dozen', 'draft', 'drama',
            'drawn', 'dream', 'dress', 'drill', 'drink', 'drive', 'drove', 'dying', 'eager', 'early',
            'earth', 'eight', 'elite', 'empty', 'enemy', 'enjoy', 'enter', 'entry', 'equal', 'error',
            'event', 'every', 'exact', 'exist', 'extra', 'faith', 'false', 'fault', 'fiber', 'field',
            'fifth', 'fifty', 'fight', 'final', 'first', 'fixed', 'flash', 'fleet', 'floor', 'focus',
            'force', 'forth', 'forty', 'forum', 'found', 'frame', 'frank', 'fraud', 'fresh', 'front',
            'fruit', 'fully', 'funny', 'giant', 'given', 'glass', 'globe', 'going', 'grace', 'grade',
            'grand', 'grant', 'grass', 'great', 'green', 'gross', 'group', 'grown', 'guard', 'guess',
            'guest', 'guide', 'happy', 'harry', 'heart', 'heavy', 'hence', 'horse', 'hotel', 'house',
            'human', 'ideal', 'image', 'index', 'inner', 'input', 'issue', 'japan', 'jimmy', 'joint',
            'jones', 'judge', 'known', 'label', 'large', 'laser', 'later', 'laugh', 'layer', 'learn',
            'lease', 'least', 'leave', 'legal', 'level', 'lever', 'light', 'limit', 'links', 'lives',
            'local', 'logic', 'loose', 'lower', 'lucky', 'lunch', 'lying', 'magic', 'major', 'maker',
            'march', 'maria', 'match', 'maybe', 'mayor', 'meant', 'media', 'metal', 'might', 'minor',
            'minus', 'mixed', 'model', 'money', 'month', 'moral', 'motor', 'mount', 'mouse', 'mouth',
            'movie', 'music', 'needs', 'never', 'newly', 'night', 'noise', 'north', 'noted', 'novel',
            'nurse', 'occur', 'ocean', 'offer', 'often', 'order', 'other', 'ought', 'paint', 'panel',
            'paper', 'party', 'peace', 'peter', 'phase', 'phone', 'photo', 'piece', 'pilot', 'pitch',
            'place', 'plain', 'plane', 'plant', 'plate', 'point', 'pound', 'power', 'press', 'price',
            'pride', 'prime', 'print', 'prior', 'prize', 'proof', 'proud', 'prove', 'queen', 'quick',
            'quiet', 'quite', 'radio', 'raise', 'range', 'rapid', 'ratio', 'reach', 'ready', 'refer',
            'right', 'rival', 'river', 'robin', 'roger', 'roman', 'rough', 'round', 'route', 'royal',
            'rural', 'scale', 'scene', 'scope', 'score', 'sense', 'serve', 'seven', 'shall', 'shape',
            'share', 'sharp', 'sheet', 'shelf', 'shell', 'shift', 'shine', 'shirt', 'shock', 'shoot',
            'short', 'shown', 'sight', 'since', 'sixth', 'sixty', 'sized', 'skill', 'sleep', 'slide',
            'small', 'smart', 'smile', 'smith', 'smoke', 'solid', 'solve', 'sorry', 'sound', 'south',
            'space', 'spare', 'speak', 'speed', 'spend', 'spent', 'split', 'spoke', 'sport', 'staff',
            'stage', 'stake', 'stand', 'start', 'state', 'steam', 'steel', 'stick', 'still', 'stock',
            'stone', 'stood', 'store', 'storm', 'story', 'strip', 'stuck', 'study', 'stuff', 'style',
            'sugar', 'suite', 'super', 'sweet', 'table', 'taken', 'taste', 'taxes', 'teach', 'teeth',
            'terry', 'texas', 'thank', 'theft', 'their', 'theme', 'there', 'these', 'thick', 'thing',
            'think', 'third', 'those', 'three', 'threw', 'throw', 'tight', 'times', 'tired', 'title',
            'today', 'topic', 'total', 'touch', 'tough', 'tower', 'track', 'trade', 'train', 'treat',
            'trend', 'trial', 'tried', 'tries', 'truck', 'truly', 'trust', 'truth', 'twice', 'under',
            'undue', 'union', 'unity', 'until', 'upper', 'upset', 'urban', 'usage', 'usual', 'valid',
            'value', 'video', 'virus', 'visit', 'vital', 'voice', 'waste', 'watch', 'water', 'wheel',
            'where', 'which', 'while', 'white', 'whole', 'whose', 'woman', 'women', 'world', 'worry',
            'worse', 'worst', 'worth', 'would', 'wound', 'write', 'wrong', 'wrote', 'yield', 'young',
            'youth', 'zebra',
            'abide', 'abler', 'abode', 'abort', 'abyss', 'acorn', 'acres', 'acted', 'adept', 'adore',
            'adorn', 'afire', 'afoot', 'agile', 'aging', 'agony', 'aisle', 'alley', 'allot', 'amass',
            'amaze', 'amino', 'amity', 'ample', 'amply', 'amuse', 'ankle', 'annex', 'annoy', 'annul',
            'anvil', 'apron', 'arbor', 'ardor', 'aroma', 'array', 'artsy', 'ashen', 'attic', 'avail',
            'avert', 'await', 'awake', 'axiom', 'azure', 'bacon', 'badge', 'bagel', 'baggy', 'balsa',
            'banal', 'banjo', 'barge', 'basal', 'basin', 'baton', 'bawdy', 'beads', 'beady', 'beard',
            'beast', 'befit', 'belch', 'belle', 'belly', 'beret', 'berth', 'beset', 'betel', 'bevel',
            'biddy', 'bigot', 'bilge', 'binge', 'biota', 'birch', 'bison', 'bitty', 'blade', 'bland',
            'blare', 'blast', 'blaze', 'bleak', 'bleed', 'blend', 'bless', 'blimp', 'bliss', 'bloom',
            'blown', 'bluer', 'bluff', 'blurt', 'blush', 'boast', 'bobby', 'bogey', 'bogus', 'bonny',
            'bonus', 'boozy', 'borax', 'bored', 'boric', 'bough', 'bowel', 'boxer', 'braid', 'brash',
            'brawl', 'brawn', 'bribe', 'bride', 'brink', 'briny', 'brisk', 'broil', 'brood', 'brook',
            'broom', 'broth', 'brunt', 'brush', 'brute', 'budge', 'buggy', 'bulky', 'bully', 'bunch',
            'bunny', 'burly', 'burnt', 'burst', 'bused', 'busty', 'butch', 'butte', 'buzzy', 'cacao',
            'cache', 'cacti', 'cadet', 'caged', 'cairn', 'camel', 'cameo', 'canny', 'canoe', 'canon',
            'caper', 'caput', 'carat', 'cargo', 'carol', 'carve', 'caste', 'cater', 'catty', 'cavil',
            'cease', 'cedar', 'cello', 'chafe', 'chaff', 'chalk', 'champ', 'chant', 'chaos', 'chard',
            'charm', 'chasm', 'cheat', 'cheek', 'cheer', 'chess', 'chevy', 'chide', 'chili', 'chill',
            'chime', 'chimp', 'chirp', 'chive', 'chock', 'choir', 'choke', 'chord', 'chore', 'chuck',
            'chump', 'chunk', 'churn', 'chute', 'cigar', 'cinch', 'civic', 'clack', 'clamp', 'clang',
            'clasp', 'cleat', 'cleft', 'cliff', 'climb', 'cling', 'clink', 'cloak', 'clone', 'clove',
            'clown', 'cluck', 'clued', 'clump', 'clung', 'cobra', 'cocoa', 'colon', 'comet', 'comfy',
            'comic', 'condo', 'conic', 'corny', 'couch', 'cough', 'coven', 'covet', 'covey', 'coyly',
            'crabs', 'crack', 'crane', 'crank', 'crass', 'crate', 'crave', 'crawl', 'craze', 'crazy',
            'creak', 'creep', 'cress', 'crest', 'crick', 'crisp', 'croak', 'crock', 'crone', 'crook',
            'crops', 'crore', 'cruet', 'crush', 'crust', 'crypt', 'cubic', 'cumin', 'cupid', 'curly',
            'curry', 'curse', 'cutie', 'cyber', 'daddy', 'dairy', 'daisy', 'dally', 'dandy', 'datum',
            'decay', 'decal', 'decor', 'decoy', 'decry', 'defer', 'deign', 'deity', 'delta', 'delve',
            'demon', 'denim', 'dense', 'depot', 'derby', 'deter', 'detox', 'deuce', 'devil', 'dewan',
            'diary', 'dicey', 'digit', 'dimly', 'diner', 'dingy', 'diode', 'dirge', 'dirty', 'disco',
            'ditch', 'ditty', 'ditto', 'dizzy', 'dodge', 'dodgy', 'dolly', 'donor', 'donut', 'dopey',
            'dough', 'dowdy', 'dowel', 'downy', 'drape', 'dread', 'dried', 'drier', 'drift', 'drone',
            'drool', 'droop', 'drops', 'dross', 'drove', 'drunk', 'dryer', 'dryly', 'ducal', 'dumbo',
            'dummy', 'dunce', 'dunes', 'dunno', 'dusky', 'dusty', 'dwarf', 'dwell', 'dwelt', 'dying',
            'easel', 'eaten', 'eater', 'eaves', 'ebony', 'eclat', 'edict', 'eerie', 'eight', 'eject',
            'elbow', 'elder', 'elect', 'elfin', 'elide', 'elope', 'elude', 'email', 'ember', 'emcee',
            'emoji', 'emote', 'enact', 'ended', 'endow', 'enema', 'envoy', 'epoch', 'epoxy', 'equip',
            'erase', 'erode', 'erred', 'erupt', 'essay', 'ether', 'ethic', 'ethos', 'evade', 'evict',
            'evoke', 'exact', 'exalt', 'excel', 'exert', 'exile', 'expat', 'expel', 'extol', 'exude',
            'exult', 'eyrie', 'fable', 'facet', 'fagot', 'faint', 'fairy', 'faker', 'fancy', 'farce',
            'fatal', 'fatty', 'fauna', 'feast', 'feign', 'feint', 'fella', 'felon', 'femme', 'femur',
            'fence', 'feral', 'ferry', 'fetal', 'fetch', 'fetid', 'fetus', 'feudo', 'fever', 'fewer',
            'fibre', 'ficus', 'fiend', 'fiery', 'filch', 'filed', 'filet', 'filmy', 'filth', 'finch',
            'finer', 'fired', 'fishy', 'fizzy', 'fjord', 'flack', 'flags', 'flair', 'flake', 'flaky',
            'flame', 'flank', 'flare', 'flask', 'flats', 'flaxy', 'flesh', 'flick', 'fling', 'flint',
            'float', 'flock', 'flood', 'flora', 'floss', 'flour', 'flout', 'fluid', 'fluke', 'flung',
            'flunk', 'flush', 'flute', 'foamy', 'focal', 'foggy', 'folio', 'folly', 'foray', 'forge',
            'forgo', 'forte', 'forum', 'fosse', 'foyer', 'frail', 'freak', 'freed', 'freer', 'frenk',
            'friar', 'fried', 'frill', 'frisk', 'frizz', 'frock', 'frond', 'frost', 'froth', 'froze',
            'frugal','frump', 'fudge', 'fugal', 'fungi', 'funky', 'furry', 'fussy', 'fusty', 'fuzzy',
            'gaffe', 'gaily', 'gamer', 'gamma', 'gamut', 'gaudy', 'gauge', 'gaunt', 'gauze', 'gavel',
            'gawky', 'gazer', 'gecko', 'geeky', 'genie', 'genre', 'genus', 'getup', 'ghost', 'ghoul',
            'giddy', 'giddy', 'glaze', 'gleam', 'glean', 'glee', 'glide', 'glint', 'gloat', 'gloom',
            'glory', 'gloss', 'glove', 'glyph', 'gnarly','gnash', 'gnome', 'godly', 'golly', 'gonna',
            'goody', 'goofy', 'goose', 'gorge', 'gotta', 'gouge', 'gourd', 'grace', 'graft', 'grail',
            'grain', 'grape', 'graph', 'grasp', 'grate', 'grave', 'gravy', 'graze', 'greed', 'greek',
            'greet', 'grief', 'grill', 'grime', 'grimy', 'grind', 'gripe', 'groan', 'groin', 'groom',
            'grope', 'grove', 'growl', 'gruel', 'gruff', 'grunt', 'guava', 'guild', 'guilt', 'guise',
            'gulch', 'gully', 'gumbo', 'gummy', 'guppy', 'gusto', 'gusty', 'gutter','gyrus', 'habit',
            'hairy', 'halve', 'handy', 'haste', 'hasty', 'hatch', 'haunt', 'haven', 'havoc', 'hazel',
            'heady', 'heave', 'hedge', 'heist', 'helix', 'hello', 'henna', 'herbs', 'heron', 'hertz',
            'hilly', 'hinge', 'hippo', 'hitch', 'hoard', 'hobby', 'homer', 'honey', 'honor', 'hoody',
            'horny', 'hound', 'hover', 'howdy', 'hubby', 'huffy', 'hulky', 'humor', 'humps', 'humid',
            'hunky', 'hurry', 'husky', 'hutch', 'hyena', 'hymns', 'hyper', 'icily', 'icing', 'idiot',
            'idler', 'igloo', 'iliac', 'imbue', 'impel', 'imply', 'inane', 'incur', 'indie', 'inept',
            'inert', 'infer', 'inlet', 'inter', 'ionic', 'irate', 'ivory', 'jabot', 'jazzy', 'jelly',
            'jenny', 'jerky', 'jewel', 'jiffy', 'jimmy', 'joker', 'jolly', 'joust', 'juicy', 'jumbo',
            'jumpy', 'junco', 'juror', 'kabob', 'kayak', 'kebab', 'khaki', 'kinky', 'kiosk', 'knack',
            'knead', 'kneel', 'knelt', 'knife', 'knack', 'knock', 'knoll', 'knots', 'known', 'koala',
            'kudos', 'label', 'laden', 'ladle', 'lager', 'lance', 'lanky', 'lapel', 'lapse', 'larch',
            'largo', 'larva', 'latch', 'later', 'lathe', 'latte', 'laugh', 'layer', 'leach', 'leafy',
            'leaky', 'leapt', 'leash', 'ledge', 'leech', 'lefty', 'leggy', 'lemma', 'lemon', 'lemur',
            'lever', 'libel', 'lilac', 'limbo', 'limen', 'liner', 'lingo', 'llama', 'loamy', 'lobby',
            'lofty', 'login', 'loopy', 'loose', 'lorry', 'loser', 'lousy', 'lover', 'lucid', 'lumpy',
            'lunar', 'lunge', 'lurch', 'lusty', 'lying', 'lymph', 'lynch', 'lyric', 'macaw', 'macho',
            'macro', 'mafia', 'mange', 'mango', 'mania', 'manic', 'manor', 'maple', 'marsh', 'mason',
            'masse', 'matey', 'mauve', 'maxim', 'mealy', 'meaty', 'medic', 'mercy', 'merge', 'merit',
            'merry', 'messy', 'meter', 'metro', 'micro', 'midst', 'mimic', 'mince', 'mirth', 'miser',
            'misty', 'miter', 'mogul', 'moist', 'moldy', 'mommy', 'moose', 'moron', 'morph', 'mossy',
            'motel', 'motif', 'motto', 'moult', 'mound', 'mourn', 'mousy', 'mover', 'moxie', 'mucus',
            'muddy', 'mufti', 'muggy', 'mulch', 'mummy', 'mural', 'murky', 'mushy', 'musky', 'musty',
            'myrrh', 'nadir', 'naive', 'nanny', 'nasal', 'nasty', 'natal', 'naval', 'navel', 'needy',
            'nerve', 'nervy', 'newer', 'nexus', 'niche', 'ninja', 'ninth', 'nitro', 'noble', 'nobly',
            'noisy', 'nomad', 'noose', 'notch', 'nudge', 'nymph', 'oaken', 'oasis', 'offal', 'olive',
            'omega', 'onset', 'opera', 'optic', 'orbit', 'organ', 'osier', 'otter', 'outdo', 'outer',
            'outgo', 'ovary', 'overt', 'oxide', 'ozone', 'paddy', 'pagan', 'paler', 'palsy', 'pamby',
            'panda', 'pandy', 'panic', 'pansy', 'papal', 'parse', 'pasta', 'paste', 'pasty', 'patch',
            'patio', 'patsy', 'patty', 'pause', 'peach', 'pearl', 'pecan', 'pedal', 'penal', 'pence',
            'penny', 'perch', 'peril', 'perky', 'pesky', 'pesto', 'petal', 'petty', 'piano', 'picky',
            'plaid', 'plank', 'plaza', 'plead', 'pleat', 'plier', 'plonk', 'pluck', 'plumb', 'plume',
            'plump', 'plunk', 'plush', 'poach', 'poker', 'polar', 'polka', 'polyp', 'poppy', 'porch',
            'porky', 'poser', 'posit', 'posse', 'potty', 'pouch', 'pouty', 'prank', 'prawn', 'preen',
            'press', 'prick', 'primp', 'prism', 'privy', 'probe', 'proem', 'promo', 'prone', 'prong',
            'prose', 'prowl', 'proxy', 'prude', 'prune', 'psalm', 'pubic', 'pudgy', 'pulse', 'punch',
            'pupal', 'pupil', 'puppy', 'purge', 'pushy', 'putty', 'pygmy', 'quack', 'quaff', 'quail',
            'qualm', 'quark', 'query', 'quest', 'queue', 'quota', 'quote', 'quoth', 'rabbi', 'rabid',
            'racer', 'radar', 'radii', 'radon', 'rainy', 'rally', 'ranch', 'randy', 'raven', 'rayon',
            'razor', 'rebel', 'rebus', 'rebut', 'recap', 'recur', 'redux', 'refer', 'regal', 'reign',
            'relax', 'relay', 'relic', 'remit', 'renal', 'renew', 'repay', 'repel', 'reply', 'rerun',
            'reset', 'resin', 'retch', 'retro', 'retry', 'revel', 'rider', 'ridge', 'rifle', 'rigid',
            'rigor', 'rinse', 'ripen', 'risen', 'risky', 'ritzy', 'roast', 'rogue', 'rookie','roost',
            'roomy', 'roost', 'rotor', 'rouge', 'rowdy', 'royal', 'rugby', 'rumba', 'rumor', 'rupee',
            'rusty', 'sable', 'sabre', 'saint', 'salad', 'salon', 'salsa', 'salty', 'salve', 'salvo',
            'sandy', 'sanky', 'sappy', 'satin', 'satyr', 'sauce', 'saucy', 'sauna', 'savor', 'savvy',
            'scald', 'scalp', 'scaly', 'scamp', 'scant', 'scare', 'scary', 'scent', 'scoff', 'scold',
            'scone', 'scoop', 'scoot', 'scope', 'scorn', 'scout', 'scowl', 'scram', 'scrap', 'scree',
            'screw', 'scrub', 'sedan', 'seize', 'semen', 'sepia', 'serif', 'setup', 'sever', 'shack',
            'shade', 'shady', 'shaft', 'shaggy','shake', 'shaky', 'shale', 'shame', 'shank', 'shawl',
            'shear', 'sheen', 'sheep', 'sheer', 'sheik', 'shine', 'shiny', 'shire', 'shirk', 'shoal',
            'shore', 'shorn', 'shout', 'shove', 'showy', 'shrub', 'shrug', 'shrub', 'shunt', 'siege',
            'sieve', 'sigma', 'silky', 'silly', 'sinew', 'siren', 'sissy', 'skate', 'skier', 'skimp',
            'skull', 'skunk', 'slack', 'slain', 'slang', 'slant', 'slash', 'slate', 'sleek', 'sleet',
            'slept', 'slice', 'slick', 'slimy', 'sling', 'slink', 'slope', 'slosh', 'sloth', 'slump',
            'smack', 'smell', 'smelt', 'smirk', 'smite', 'smith', 'smock', 'snack', 'snafu', 'snail',
            'snake', 'snare', 'snarl', 'sneak', 'sneer', 'snide', 'sniff', 'snore', 'snort', 'snout',
            'snowy', 'snuff', 'soapy', 'sober', 'solar', 'sonar', 'sonic', 'sooth', 'sooty', 'soppy',
            'sorely','spade', 'spank', 'spark', 'spasm', 'spawn', 'spear', 'speck', 'spell', 'spelt',
            'spice', 'spicy', 'spied', 'spiel', 'spike', 'spiky', 'spill', 'spine', 'spine', 'spiny',
            'spite', 'spoil', 'spoke', 'spoof', 'spook', 'spool', 'spoon', 'spore', 'spout', 'spray',
            'spree', 'sprig', 'spurt', 'squad', 'squat', 'squid', 'staid', 'stain', 'stair', 'stale',
            'stalk', 'stall', 'stamp', 'stank', 'stare', 'stark', 'stash', 'stave', 'steak', 'steal',
            'steam', 'steed', 'steep', 'steer', 'stems', 'steno', 'stern', 'stiff', 'sting', 'stink',
            'stint', 'stoic', 'stoke', 'stomp', 'stony', 'stool', 'stoop', 'stork', 'stout', 'stove',
            'straw', 'stray', 'strew', 'stuck', 'stump', 'stung', 'stunk', 'stunt', 'suave', 'sugar',
            'surge', 'surly', 'sushi', 'swami', 'swamp', 'swank', 'swarm', 'swath', 'swear', 'sweat',
            'sweep', 'swell', 'swept', 'swift', 'swill', 'swine', 'swing', 'swipe', 'swirl', 'swish',
            'swoon', 'swoop', 'sword', 'swore', 'sworn', 'swung', 'synod', 'syrup', 'tabby', 'tacit',
            'tacky', 'taffy', 'taint', 'taker', 'talon', 'tamer', 'tango', 'tangy', 'taper', 'tapir',
            'tardy', 'tarts', 'taunt', 'tawny', 'tease', 'teddy', 'tempo', 'tenet', 'tenor', 'tense',
            'tenth', 'tepee', 'tepid', 'theta', 'thief', 'thigh', 'thorn', 'those', 'thong', 'three',
            'throe', 'thumb', 'thump', 'tiara', 'tidal', 'tiger', 'tilts', 'timid', 'tipsy', 'toast',
            'toddy', 'token', 'tonal', 'tonic', 'tooth', 'topaz', 'torch', 'torso', 'totem', 'toxin',
            'tract', 'trashy','trawl', 'trays', 'treks', 'triad', 'tribe', 'trice', 'trill', 'tripe',
            'trite', 'troll', 'troop', 'trope', 'troth', 'trout', 'truce', 'trunk', 'truss', 'tubal',
            'tulip', 'tumor', 'tuner', 'tunic', 'turbo', 'tutor', 'twang', 'tweak', 'tweed', 'twerp',
            'tying', 'udder', 'ulcer', 'ultra', 'umbra', 'uncle', 'uncut', 'unfit', 'unify', 'unite',
            'unity', 'unlit', 'unmet', 'unsay', 'untie', 'unwed', 'unzip', 'usher', 'usurp', 'utter',
            'uvula', 'vague', 'valet', 'valor', 'valve', 'vapid', 'vault', 'vaunt', 'vegan', 'reign',
            'veldt', 'venom', 'venue', 'verge', 'verse', 'vigor', 'vinca', 'vinyl', 'viola', 'viper',
            'visor', 'vista', 'vivid', 'vixen', 'vocal', 'vodka', 'vogue', 'voila', 'vouch', 'vowel',
            'vulva', 'wacky', 'wader', 'wafer', 'wager', 'wagon', 'waist', 'walky', 'waltz', 'wanna',
            'wardy', 'wares', 'warps', 'warty', 'weary', 'weave', 'webby', 'wedge', 'weedy', 'weird',
            'welch', 'wells', 'wench', 'whale', 'wheat', 'whiff', 'whine', 'whiny', 'whirl', 'whisk',
            'wider', 'widow', 'width', 'wield', 'wilds', 'wills', 'wimpy', 'wince', 'winch', 'winds',
            'windy', 'wings', 'witch', 'witty', 'woken', 'wolfy', 'woman', 'woody', 'woozy', 'wordy',
            'works', 'worms', 'worst', 'wrack', 'wrath', 'wreak', 'wreck', 'wrest', 'wring', 'wrist',
            'xenon', 'yacht', 'yearn', 'yeast', 'yodel', 'yokel', 'yummy', 'zappy', 'zesty', 'zippy',
            'zloty', 'zonal', 'zones',
            'acrid', 'addax', 'adage', 'adder', 'addon', 'adobe', 'aegis', 'afoot', 'agave', 'agate',
            'aider', 'aioli', 'aitch', 'algae', 'alien', 'align', 'alibi', 'alloy', 'aloft', 'alpha',
            'alter', 'amend', 'amine', 'amuse', 'angel', 'anger', 'antic', 'anvil', 'aorta', 'aphid',
            'arbor', 'atoll', 'augur', 'avian', 'awash', 'awful', 'axial', 'bacon', 'badge', 'balmy',
            'bandy', 'batik', 'bayou', 'beady', 'begin', 'being', 'belay', 'benne', 'berry', 'billy',
            'black', 'blank', 'bleat', 'bleep', 'blitz', 'bloat', 'bloke', 'blond', 'blown', 'blues',
            'blunt', 'boggy', 'bolts', 'bonds', 'bongo', 'books', 'boots', 'bored', 'borns', 'botch',
            'bough', 'bower', 'bowls', 'boyar', 'braze', 'break', 'breed', 'brews', 'bride', 'brine',
            'bring', 'brisk', 'broil', 'broke', 'brook', 'brown', 'budge', 'build', 'bulge', 'bumpy',
            'buret', 'burro', 'bylaw', 'byway', 'cabal', 'cabin', 'caddy', 'calve', 'candy', 'canny',
            'canst', 'carat', 'cargo', 'carry', 'carve', 'cedar', 'chafe', 'chasm', 'cheap', 'chief',
            'child', 'china', 'chunk', 'cider', 'civet', 'claim', 'clamp', 'clank', 'clash', 'clasp',
            'class', 'claws', 'clean', 'cleft', 'clerk', 'click', 'climb', 'cline', 'clods', 'clogs',
            'cloth', 'cloud', 'clout', 'clubs', 'cluck', 'coals', 'coats', 'codex', 'coils', 'coins',
            'combs', 'comma', 'coney', 'cooks', 'coped', 'coral', 'cords', 'cores', 'corps', 'costs',
            'coupe', 'cower', 'crack', 'cramp', 'crate', 'crawl', 'creek', 'crews', 'crops', 'crowd',
            'crude', 'cruel', 'crumb', 'cubed', 'cuffs', 'curds', 'cured', 'curls', 'curvy', 'cushy',
            'darts', 'dates', 'daunt', 'deals', 'debts', 'decks', 'deeds', 'deems', 'demon', 'denim',
            'depot', 'desks', 'digit', 'dingo', 'dirty', 'dodge', 'dolce', 'donor', 'dorky', 'doses',
            'dotes', 'drags', 'drain', 'drape', 'draws', 'dream', 'dress', 'dried', 'drink', 'drips',
            'drone', 'drops', 'drugs', 'drums', 'dryad', 'ducat', 'ducks', 'duets', 'dulls', 'dunks',
            'duple', 'dweeb', 'early', 'earns', 'eater', 'ebbed', 'edged', 'edger', 'edges', 'edits',
            'eight', 'elate', 'elfin', 'elite', 'elope', 'elude', 'elves', 'emery', 'emirs', 'emits',
            'ended', 'endow', 'enemy', 'enjoy', 'ensue', 'enter', 'envoy', 'epoch', 'equip', 'error',
            'essay', 'ethyl', 'evade', 'event', 'every', 'exact', 'exams', 'exile', 'extra', 'exude',
            'fable', 'faced', 'facet', 'facts', 'faded', 'fails', 'faint', 'fairy', 'faith', 'falls',
            'false', 'famed', 'fancy', 'fangs', 'farce', 'fared', 'fatal', 'fates', 'fatty', 'fault',
            'favor', 'feast', 'feats', 'feeds', 'feels', 'feign', 'feint', 'femur', 'fends', 'ferns',
            'ferry', 'fetch', 'feuds', 'fever', 'fewer', 'fibre', 'field', 'fiend', 'fifty', 'fight',
            'filch', 'filed', 'fills', 'films', 'filth', 'final', 'finds', 'fined', 'finer', 'fires',
            'firms', 'first', 'fixes', 'flags', 'flair', 'flake', 'flame', 'flare', 'flash', 'flask',
            'flats', 'flaxy', 'fleas', 'fleck', 'flesh', 'flies', 'fling', 'flint', 'float', 'flock',
            'flood', 'floor', 'floss', 'flour', 'flows', 'fluid', 'flush', 'flute', 'foggy', 'folds',
            'folks', 'folly', 'fonts', 'foods', 'fools', 'force', 'forge', 'forms', 'forth', 'forty',
            'forum', 'fossil','fouls', 'found', 'foxes', 'foyer', 'frail', 'frame', 'frank', 'fraud',
            'fresh', 'friar', 'fried', 'front', 'frost', 'froze', 'fruit', 'fuels', 'fully', 'funds',
            'funny', 'furry', 'fused', 'fuses', 'fuzzy', 'gains', 'gaits', 'gales', 'gamma', 'gangs',
            'gases', 'gates', 'gauge', 'gaunt', 'gavel', 'gazer', 'gears', 'genes', 'genre', 'genus',
            'germs', 'ghost', 'giant', 'gifts', 'girls', 'girth', 'given', 'gives', 'gland', 'glare',
            'glass', 'gleam', 'glean', 'glide', 'globe', 'gloom', 'glory', 'gloss', 'glove', 'glued',
            'gnome', 'goals', 'goats', 'godly', 'going', 'goods', 'goons', 'gorge', 'grade', 'grain',
            'grams', 'grand', 'grant', 'grape', 'graph', 'grasp', 'grass', 'grate', 'grave', 'gravy',
            'grays', 'graze', 'great', 'greed', 'green', 'greet', 'grief', 'grill', 'grime', 'grind',
            'gripe', 'groan', 'groom', 'gross', 'group', 'grove', 'growl', 'grown', 'grows', 'gruel',
            'guard', 'guava', 'guess', 'guest', 'guide', 'guild', 'guilt', 'guise', 'gulps', 'gusty',
            'gypsy', 'hairs', 'halls', 'halts', 'hands', 'handy', 'hangs', 'happy', 'harsh', 'haste',
            'hasty', 'hatch', 'hated', 'hater', 'hauls', 'haunt', 'haven', 'hawks', 'hazel', 'heads',
            'heals', 'heaps', 'heard', 'hears', 'heart', 'heats', 'heavy', 'hedge', 'heeds', 'heels',
            'hefty', 'heirs', 'hello', 'helps', 'hence', 'herbs', 'herds', 'hills', 'hilly', 'hints',
            'hippy', 'hired', 'hitch', 'hobby', 'holds', 'holes', 'holly', 'homes', 'honey', 'honor',
            'hooks', 'hoped', 'hopes', 'horns', 'horse', 'hosts', 'hotel', 'hound', 'hours', 'house',
            'human', 'humid', 'humor', 'humps', 'hunts', 'hurry', 'hurts', 'hyena', 'hyper', 'icing',
            'ideas', 'idiom', 'idiot', 'idyll', 'image', 'imago', 'immix', 'imped', 'inane', 'incur',
            'index', 'indie', 'inert', 'infer', 'inner', 'input', 'intro', 'ionic', 'irate', 'irked',
            'irony', 'issue', 'ivory', 'jazzy', 'jeans', 'jelly', 'jenny', 'jerks', 'jerky', 'jewel',
            'jiffy', 'joins', 'joint', 'joker', 'jolly', 'jolts', 'joust', 'judge', 'juice', 'juicy',
            'jumbo', 'jumps', 'jumpy', 'juror', 'karst', 'kayak', 'keels', 'keeps', 'khaki', 'kicks',
            'kills', 'kinds', 'kings', 'kiosk', 'kites', 'knack', 'knead', 'kneel', 'knelt', 'knife',
            'knobs', 'knock', 'knoll', 'knots', 'kudos', 'label', 'labor', 'laced', 'lacks', 'laden',
            'lands', 'lanes', 'lapel', 'lapse', 'large', 'laser', 'latch', 'later', 'latex', 'lathe',
            'lauds', 'leads', 'leafy', 'leaks', 'leapt', 'learn', 'lease', 'least', 'leave', 'ledge',
            'legal', 'lemon', 'level', 'lever', 'light', 'liked', 'liken', 'lilac', 'limbs', 'limit',
            'limps', 'lined', 'linen', 'liner', 'lines', 'links', 'lions', 'lists', 'liter', 'lived',
            'liver', 'lives', 'llama', 'loads', 'loafs', 'loams', 'loans', 'lobby', 'local', 'locks',
            'lodge', 'lofty', 'logic', 'logos', 'looks', 'loops', 'lords', 'lorry', 'loser', 'loses',
            'lousy', 'loved', 'lover', 'loves', 'lower', 'lucid', 'lucky', 'lumps', 'lumpy', 'lunar',
            'lunch', 'lunge', 'lungs', 'lurch', 'lyric', 'macro', 'mafia', 'magic', 'mails', 'maims',
            'major', 'maker', 'makes', 'males', 'malls', 'manga', 'mango', 'manor', 'maple', 'march',
            'marks', 'marsh', 'masks', 'match', 'mated', 'mates', 'mauve', 'maxim', 'mayor', 'meals',
            'means', 'meant', 'meats', 'media', 'meets', 'melon', 'mercy', 'merge', 'merit', 'merry',
            'messy', 'metal', 'meter', 'metro', 'micro', 'midst', 'might', 'miles', 'mills', 'mimic',
            'minds', 'mined', 'miner', 'mines', 'minor', 'minus', 'mired', 'mirth', 'miser', 'misty',
            'mites', 'mixed', 'mixer', 'moans', 'moats', 'mocks', 'model', 'modem', 'modes', 'mogul',
            'moist', 'molar', 'moldy', 'money', 'monks', 'month', 'moods', 'moody', 'moose', 'moral',
            'moron', 'mossy', 'motel', 'moths', 'motor', 'motto', 'mound', 'mount', 'mourn', 'mouse',
            'mouth', 'moved', 'mover', 'moves', 'movie', 'mowed', 'mower', 'mucus', 'muddy', 'mulch',
            'mules', 'mural', 'murky', 'music', 'musty', 'muted', 'myths', 'nails', 'naive', 'named',
            'names', 'nanny', 'naval', 'necks', 'needs', 'nerve', 'nervy', 'nests', 'never', 'newly',
            'nexus', 'niche', 'night', 'ninja', 'noble', 'nobly', 'noise', 'noisy', 'nomad', 'nooks',
            'norms', 'north', 'noted', 'notes', 'novel', 'nudge', 'nurse', 'nutty', 'nylon', 'oaken',
            'oasis', 'occur', 'ocean', 'oddly', 'offer', 'often', 'oinks', 'olive', 'omega', 'onset',
            'opera', 'opted', 'optic', 'orbit', 'order', 'organ', 'other', 'otter', 'ought', 'ounce',
            'outer', 'outgo', 'ovary', 'overt', 'owned', 'owner', 'oxide', 'ozone', 'paced', 'paces',
            'packs', 'pages', 'pails', 'pains', 'paint', 'pairs', 'palms', 'panel', 'panes', 'panic',
            'pants', 'paper', 'parks', 'party', 'paste', 'patch', 'paths', 'patio', 'pause', 'paved',
            'paves', 'pawed', 'payer', 'peace', 'peach', 'peaks', 'pearl', 'pears', 'pecan', 'pedal',
            'peeks', 'peels', 'peers', 'penal', 'pence', 'penny', 'perch', 'peril', 'perks', 'perky',
            'pesky', 'pesto', 'petal', 'petty', 'phase', 'phone', 'photo', 'piano', 'picks', 'picky',
            'piece', 'piers', 'pigmy', 'piled', 'piles', 'pills', 'pilot', 'pinch', 'pined', 'pines',
            'pints', 'piper', 'pipes', 'pitch', 'pitas', 'pivot', 'pixel', 'pizza', 'place', 'plaid',
            'plain', 'plane', 'plank', 'plans', 'plant', 'plate', 'playa', 'plaza', 'plead', 'pleas',
            'pleat', 'plied', 'plods', 'plops', 'plots', 'plows', 'ploys', 'pluck', 'plugs', 'plumb',
            'plume', 'plump', 'plums', 'plunk', 'plush', 'poems', 'poets', 'point', 'poise', 'poker',
            'polar', 'poles', 'polls', 'polyp', 'ponds', 'pools', 'poppy', 'porch', 'pored', 'pores',
            'ports', 'posed', 'poses', 'poser', 'posts', 'potty', 'pouch', 'pouty', 'power', 'prams',
            'prank', 'prawn', 'prays', 'press', 'preys', 'price', 'pride', 'prime', 'print', 'prior',
            'prism', 'privy', 'prize', 'probe', 'prods', 'promo', 'prone', 'proof', 'props', 'prose',
            'proud', 'prove', 'prowl', 'prude', 'prune', 'psalm', 'pubic', 'pulls', 'pulps', 'pulse',
            'pumps', 'punch', 'pupil', 'puppy', 'purge', 'purrs', 'pushy', 'putts', 'putty', 'pygmy',
            'quack', 'qualm', 'queen', 'query', 'quest', 'queue', 'quick', 'quiet', 'quilt', 'quirk',
            'quota', 'quote', 'quoth', 'rabbi', 'rabid', 'raced', 'racer', 'races', 'racks', 'radar',
            'radio', 'raids', 'rails', 'rains', 'rainy', 'raise', 'rally', 'ranch', 'range', 'ranks',
            'rapid', 'rated', 'rates', 'ratio', 'raved', 'raven', 'razor', 'reach', 'reads', 'ready',
            'realm', 'reams', 'reaps', 'rebel', 'rebut', 'recap', 'reeds', 'reefs', 'reeks', 'reels',
            'regal', 'reign', 'reins', 'relax', 'relay', 'relic', 'remit', 'renal', 'renew', 'rents',
            'repay', 'repel', 'reply', 'rerun', 'reset', 'resin', 'rests', 'retro', 'retry', 'revel',
            'ridge', 'rifle', 'rigid', 'rigor', 'riled', 'rinds', 'rings', 'rinse', 'riots', 'ripen',
            'risen', 'rises', 'risks', 'risky', 'rites', 'ritzy', 'rival', 'river', 'roads', 'roams',
            'roars', 'roast', 'robes', 'robot', 'rocks', 'rocky', 'rogue', 'roles', 'rolls', 'roman',
            'roofs', 'rooms', 'roomy', 'roots', 'roped', 'ropes', 'roses', 'rotor', 'rouge', 'rough',
            'round', 'route', 'rowdy', 'rowed', 'royal', 'ruins', 'ruled', 'ruler', 'rules', 'rumba',
            'rumor', 'rupee', 'rural', 'rusty', 'saber', 'sable', 'sadly', 'saint', 'salad', 'sales',
            'salon', 'salsa', 'salty', 'salve', 'salvo', 'sands', 'sandy', 'saner', 'sauce', 'saucy',
            'sauna', 'savor', 'savvy', 'scale', 'scalp', 'scaly', 'scamp', 'scant', 'scare', 'scarf',
            'scary', 'scene', 'scent', 'score', 'scout', 'scowl', 'scram', 'scrap', 'screw', 'scrub',
            'seals', 'seams', 'seats', 'seeds', 'seedy', 'seeks', 'seems', 'seize', 'sense', 'serif',
            'serve', 'setup', 'seven', 'sever', 'shack', 'shade', 'shady', 'shaft', 'shake', 'shaky',
            'shale', 'shall', 'shame', 'shape', 'share', 'sharp', 'shave', 'shawl', 'shear', 'sheen',
            'sheep', 'sheer', 'sheet', 'shelf', 'shell', 'shift', 'shine', 'shiny', 'ships', 'shire',
            'shirk', 'shirt', 'shock', 'shoes', 'shone', 'shook', 'shoot', 'shops', 'shore', 'short',
            'shots', 'shout', 'shove', 'shown', 'shows', 'showy', 'shrub', 'shrug', 'shunt', 'sides',
            'siege', 'sieve', 'sighs', 'sight', 'sigma', 'signs', 'silky', 'silly', 'since', 'sinew',
            'siren', 'sites', 'sixth', 'sixty', 'sized', 'sizes', 'skate', 'skill', 'skimp', 'skins',
            'skirt', 'skull', 'skunk', 'slack', 'slain', 'slang', 'slant', 'slash', 'slate', 'slats',
            'sleek', 'sleep', 'sleet', 'slept', 'slice', 'slick', 'slide', 'slime', 'slimy', 'sling',
            'slink', 'slope', 'slots', 'sloth', 'slump', 'slung', 'smack', 'small', 'smart', 'smash',
            'smell', 'smile', 'smirk', 'smith', 'smoke', 'smoky', 'snack', 'snail', 'snake', 'snare',
            'sneak', 'sneer', 'snide', 'sniff', 'snore', 'snort', 'snout', 'snowy', 'snuff', 'soapy',
            'sober', 'socks', 'softy', 'soils', 'solar', 'solid', 'solve', 'sonar', 'songs', 'sonic',
            'sorry', 'sorts', 'souls', 'sound', 'south', 'space', 'spade', 'spare', 'spark', 'spawn',
            'speak', 'spear', 'speck', 'specs', 'speed', 'spell', 'spend', 'spent', 'spice', 'spicy',
            'spied', 'spiel', 'spike', 'spill', 'spine', 'spiny', 'split', 'spoke', 'spoof', 'spook',
            'spool', 'spoon', 'spore', 'sport', 'spots', 'spout', 'spray', 'spree', 'sprig', 'spurt',
            'squad', 'squat', 'squid', 'stabs', 'stack', 'staff', 'stage', 'staid', 'stain', 'stair',
            'stake', 'stale', 'stalk', 'stall', 'stamp', 'stand', 'stank', 'stare', 'stark', 'stars',
            'start', 'stash', 'state', 'stays', 'steak', 'steal', 'steam', 'steel', 'steep', 'steer',
            'stems', 'steps', 'stern', 'stews', 'stick', 'stiff', 'still', 'sting', 'stink', 'stint',
            'stock', 'stoic', 'stoke', 'stole', 'stomp', 'stone', 'stony', 'stood', 'stool', 'stoop',
            'stops', 'store', 'stork', 'storm', 'story', 'stout', 'stove', 'straw', 'stray', 'strip',
            'strew', 'stuck', 'study', 'stuff', 'stump', 'stung', 'stunk', 'stunt', 'style', 'suave',
            'suing', 'suits', 'suite', 'sulks', 'sulky', 'sunny', 'super', 'surge', 'surly', 'sushi',
            'swamp', 'swank', 'swarm', 'swath', 'swear', 'sweat', 'sweep', 'sweet', 'swell', 'swept',
            'swift', 'swill', 'swine', 'swing', 'swipe', 'swirl', 'swish', 'swoon', 'swoop', 'sword',
            'swore', 'sworn', 'swung', 'syrup', 'tabby', 'table', 'tacit', 'tacky', 'taint', 'taken',
            'tales', 'talks', 'talon', 'tamed', 'tamer', 'tango', 'tangy', 'tanks', 'taper', 'tapes',
            'tardy', 'tasks', 'taste', 'tasty', 'taunt', 'taxes', 'teach', 'teams', 'tears', 'tease',
            'teddy', 'teens', 'teeth', 'tempo', 'tenet', 'tenor', 'tense', 'tenth', 'tents', 'tepid',
            'terms', 'tests', 'texts', 'thank', 'theft', 'their', 'theme', 'there', 'these', 'thick',
            'thief', 'thigh', 'thing', 'think', 'third', 'thorn', 'those', 'three', 'threw', 'throw',
            'thugs', 'thumb', 'tidal', 'tides', 'tiger', 'tight', 'tiles', 'tilts', 'timid', 'times',
            'tints', 'tipsy', 'tired', 'titan', 'title', 'toast', 'today', 'token', 'tolls', 'tonal',
            'toned', 'tones', 'tonic', 'tools', 'tooth', 'topaz', 'topic', 'torch', 'torso', 'total',
            'totem', 'touch', 'tough', 'tours', 'towel', 'tower', 'towns', 'toxic', 'toxin', 'trace',
            'track', 'trade', 'trail', 'train', 'trait', 'tramp', 'traps', 'trash', 'trawl', 'tread',
            'treat', 'treks', 'trend', 'triad', 'trial', 'tribe', 'trick', 'tried', 'tries', 'trill',
            'trims', 'tripe', 'trite', 'troll', 'troop', 'trope', 'troth', 'trots', 'trout', 'truce',
            'truck', 'truly', 'trump', 'trunk', 'truss', 'trust', 'truth', 'tulip', 'tumor', 'tuned',
            'tuner', 'tunes', 'tunic', 'turbo', 'turns', 'tusks', 'tutor', 'twang', 'tweak', 'tweed',
            'twerp', 'twice', 'twigs', 'twill', 'twine', 'twins', 'twirl', 'twist', 'tying', 'typed',
            'types', 'udder', 'ulcer', 'ultra', 'umbra', 'uncle', 'uncut', 'under', 'undid', 'undue',
            'unfit', 'unify', 'union', 'unite', 'unity', 'unlit', 'unmet', 'until', 'untie', 'unwed',
            'unzip', 'upper', 'upset', 'urban', 'urged', 'usage', 'usher', 'usurp', 'usual', 'utter',
            'uvula', 'vague', 'valet', 'valid', 'valor', 'valve', 'vapid', 'vault', 'vaunt', 'vegan',
            'veils', 'veins', 'veldt', 'venom', 'venue', 'verbs', 'verge', 'verse', 'video', 'vigor',
            'vines', 'vinyl', 'viola', 'viper', 'viral', 'virus', 'visor', 'visit', 'vista', 'vital',
            'vivid', 'vixen', 'vocal', 'vodka', 'vogue', 'voice', 'voila', 'volts', 'voted', 'voter',
            'votes', 'vouch', 'vowed', 'vowel', 'wacky', 'waded', 'wader', 'wafer', 'waged', 'wager',
            'wages', 'wagon', 'waist', 'walks', 'walls', 'waltz', 'wands', 'wanna', 'wants', 'wards',
            'wares', 'warns', 'waste', 'watch', 'water', 'waved', 'waver', 'waves', 'weary', 'weave',
            'wedge', 'weeds', 'weedy', 'weeks', 'weigh', 'weird', 'wells', 'wench', 'whale', 'wheat',
            'wheel', 'where', 'which', 'while', 'whine', 'whiny', 'whirl', 'whisk', 'white', 'whole',
            'whose', 'widen', 'wider', 'widow', 'width', 'wield', 'wilds', 'wimpy', 'wince', 'winch',
            'winds', 'windy', 'wines', 'wings', 'wired', 'wires', 'witch', 'witty', 'woken', 'women',
            'woody', 'woozy', 'words', 'wordy', 'works', 'world', 'worms', 'worry', 'worse', 'worst',
            'worth', 'would', 'wound', 'wrack', 'wrath', 'wreak', 'wreck', 'wrest', 'wring', 'wrist',
            'write', 'wrong', 'wrote', 'yacht', 'yards', 'yearn', 'years', 'yeast', 'yield', 'young',
            'yours', 'youth', 'zappy', 'zesty', 'zippy', 'zloty', 'zonal', 'zones',
            'abaft', 'abase', 'abash', 'abate', 'abbey', 'abbot', 'abhor', 'ablow', 'abner', 'abode',
            'abort', 'about', 'above', 'abuse', 'abyss', 'acids', 'ackee', 'acmes', 'acned', 'acorn',
            'acted', 'actin', 'acute', 'adage', 'added', 'adder', 'addle', 'adept', 'adieu', 'adios',
            'admin', 'admit', 'adobe', 'adopt', 'adore', 'adorn', 'adult', 'aegis', 'aeons', 'afire',
            'afoot', 'afoul', 'after', 'again', 'agape', 'agate', 'agave', 'agent', 'aging', 'aglow',
            'agony', 'agree', 'ahead', 'ahold', 'aided', 'aider', 'aimed', 'aimer', 'aired', 'aisle',
            'alarm', 'album', 'alder', 'alert', 'algae', 'alias', 'alibi', 'alien', 'align', 'alike',
            'aline', 'alive', 'allay', 'alley', 'allot', 'allow', 'alloy', 'aloft', 'alone', 'along',
            'aloof', 'aloud', 'alpha', 'altar', 'alter', 'amaze', 'amber', 'amble', 'amend', 'amino',
            'amiss', 'amity', 'among', 'amour', 'ample', 'amply', 'amuse', 'angel', 'anger', 'angle',
            'angry', 'angst', 'anime', 'anion', 'anise', 'ankle', 'annex', 'annoy', 'annul', 'antic',
            'anvil', 'aorta', 'apart', 'aphid', 'aping', 'apnea', 'apple', 'apply', 'apron', 'aptly',
            'arbor', 'ardor', 'arena', 'argue', 'arise', 'armed', 'armor', 'aroma', 'arose', 'array',
            'arrow', 'arson', 'artsy', 'ashen', 'ashes', 'aside', 'asset', 'atlas', 'atone', 'attic',
            'audio', 'audit', 'auger', 'augur', 'aunts', 'aunty', 'avail', 'avast', 'avert', 'avian',
            'avoid', 'await', 'awake', 'award', 'aware', 'awful', 'axial', 'axiom', 'azure', 'babel',
            'backs', 'bacon', 'badge', 'badly', 'bagel', 'baggy', 'baits', 'baked', 'baker', 'bakes',
            'balks', 'balky', 'balls', 'balms', 'balmy', 'balsa', 'banal', 'bands', 'bandy', 'banes',
            'bangs', 'banjo', 'banks', 'barbs', 'bards', 'bared', 'bares', 'barge', 'barks', 'barmy',
            'barns', 'baron', 'barre', 'basal', 'based', 'bases', 'basic', 'basil', 'basin', 'basis',
            'baste', 'batch', 'bated', 'bathe', 'baths', 'batik', 'baton', 'batty', 'baulk', 'bawdy',
            'bawls', 'bayou', 'beads', 'beady', 'beaks', 'beams', 'beano', 'beans', 'beard', 'bears',
            'beast', 'beats', 'beaus', 'beaut', 'beaux', 'bebop', 'bedew', 'beech', 'beefs', 'beefy',
            'beeps', 'beers', 'beery', 'beets', 'befit', 'began', 'beget', 'begin', 'begot', 'begun',
            'beige', 'being', 'belay', 'belch', 'belie', 'belle', 'bells', 'belly', 'below', 'belts',
            'bench', 'bends', 'bendy', 'benne', 'beret', 'bergs', 'berry', 'berth', 'beset', 'betel',
            'bevel', 'bible', 'bicep', 'biddy', 'bided', 'bikes', 'bilge', 'bills', 'billy', 'bimbo',
            'binds', 'binge', 'bingo', 'biome', 'biota', 'bipod', 'birch', 'birds', 'birth', 'bison',
            'biter', 'bites', 'bitsy', 'bitty', 'blade', 'bland', 'blank', 'blare', 'blast', 'blaze',
            'bleak', 'bleat', 'bleed', 'bleep', 'blend', 'bless', 'blimp', 'blind', 'bling', 'blini',
            'blink', 'bliss', 'blitz', 'bloat', 'blobs', 'block', 'blocs', 'bloke', 'blond', 'blood',
            'bloom', 'blown', 'blows', 'bluer', 'blues', 'bluff', 'blunt', 'blurb', 'blurs', 'blurt',
            'blush', 'board', 'boars', 'boast', 'boats', 'bobby', 'boded', 'bogey', 'boggy', 'bogus',
            'boils', 'bolls', 'bolts', 'bombs', 'bonds', 'boned', 'bones', 'bongo', 'bonks', 'bonny',
            'bonus', 'booby', 'books', 'booms', 'boons', 'boost', 'booth', 'boots', 'booty', 'booze',
            'boozy', 'borax', 'bored', 'borer', 'bores', 'borne', 'boron', 'bosom', 'bossy', 'botch',
            'bough', 'boule', 'bound', 'bouts', 'bowed', 'bowel', 'bower', 'bowls', 'boxed', 'boxer',
            'boxes', 'brace', 'bract', 'brags', 'braid', 'brain', 'brake', 'brand', 'brash', 'brass',
            'brave', 'bravo', 'brawl', 'brawn', 'brays', 'bread', 'break', 'breed', 'brews', 'bribe',
            'brick', 'bride', 'brief', 'brine', 'bring', 'brink', 'briny', 'brisk', 'broad', 'broil',
            'broke', 'brood', 'brook', 'broom', 'broth', 'brown', 'brows', 'brush', 'brunt', 'brute',
            'bucks', 'buddy', 'budge', 'buffs', 'buggy', 'bugle', 'build', 'built', 'bulbs', 'bulge',
            'bulks', 'bulky', 'bulls', 'bully', 'bumps', 'bumpy', 'bunch', 'bunks', 'bunny', 'bunts',
            'buoys', 'burly', 'burns', 'burnt', 'burps', 'burro', 'burst', 'busby', 'buses', 'bushy',
            'busts', 'busty', 'butch', 'buyer', 'bylaw', 'bytes', 'byway', 'cabal', 'cabin', 'cable',
            'cacao', 'cache', 'cacti', 'caddy', 'cadet', 'cadge', 'caged', 'cages', 'cairn', 'caked',
            'cakes', 'calls', 'calms', 'calve', 'camel', 'cameo', 'camps', 'candy', 'canes', 'canid',
            'canny', 'canoe', 'canon', 'canto', 'cants', 'caper', 'capes', 'capon', 'caput', 'carat',
            'cards', 'cared', 'carer', 'cares', 'cargo', 'carob', 'carol', 'carry', 'carts', 'carve',
            'cases', 'caste', 'casts', 'catch', 'cater', 'catty', 'cause', 'caves', 'cavil', 'cease',
            'cedar', 'cells', 'cello', 'cents', 'chafe', 'chaff', 'chain', 'chair', 'chalk', 'champ',
            'chant', 'chaos', 'chaps', 'chard', 'charm', 'chart', 'chase', 'chasm', 'cheap', 'cheat',
            'check', 'cheek', 'cheer', 'chess', 'chest', 'chick', 'chide', 'chief', 'child', 'chili',
            'chill', 'chime', 'chimp', 'china', 'chins', 'chips', 'chirp', 'chive', 'chock', 'choir',
            'choke', 'chomp', 'chops', 'chord', 'chore', 'chose', 'chuck', 'chug', 'chump', 'chunk',
            'churn', 'chute', 'cider', 'cigar', 'cinch', 'circa', 'cisco', 'cited', 'cites', 'civet',
            'civic', 'civil', 'clack', 'claim', 'clamp', 'clams', 'clang', 'clank', 'clans', 'claps',
            'clash', 'clasp', 'class', 'claws', 'clays', 'clean', 'clear', 'cleat', 'cleft', 'clerk',
            'click', 'cliff', 'climb', 'cling', 'clink', 'clips', 'cloak', 'clock', 'clods', 'clogs',
            'clone', 'close', 'cloth', 'cloud', 'clout', 'clove', 'clown', 'clubs', 'cluck', 'clued',
            'clues', 'clump', 'clung', 'clunk', 'coach', 'coals', 'coast', 'coats', 'cobra', 'cocoa',
            'coded', 'codes', 'codex', 'coils', 'coins', 'colas', 'colon', 'color', 'colts', 'combs',
            'comer', 'comes', 'comet', 'comfy', 'comic', 'comma', 'condo', 'cones', 'conic', 'conte',
            'cooed', 'cooks', 'cools', 'coops', 'coord', 'coped', 'copes', 'copse', 'coral', 'cords',
            'cores', 'corgi', 'corns', 'corny', 'corps', 'costs', 'couch', 'cough', 'could', 'count',
            'coupe', 'coups', 'court', 'cover', 'coven', 'covet', 'covey', 'cowed', 'cower', 'coyly',
            'cozen', 'crabs', 'crack', 'craft', 'crags', 'cramp', 'crane', 'crank', 'craps', 'crass',
            'crate', 'crave', 'crawl', 'craze', 'crazy', 'creak', 'cream', 'credo', 'creed', 'creek',
            'creep', 'creme', 'crept', 'cress', 'crest', 'crews', 'crick', 'cried', 'crier', 'cries',
            'crime', 'crimp', 'crisp', 'croak', 'crock', 'croft', 'crone', 'crony', 'crook', 'crops',
            'cross', 'crowd', 'crown', 'crude', 'cruel', 'cruet', 'crumb', 'crush', 'crust', 'crypt',
            'cubed', 'cubes', 'cubic', 'cuffs', 'culls', 'cumin', 'cunts', 'cupid', 'curds', 'cured',
            'cures', 'curls', 'curly', 'curry', 'curse', 'curve', 'curvy', 'cushy', 'cutie', 'cyber',
            'cycle', 'cynic', 'daddy', 'daily', 'dairy', 'daisy', 'dally', 'dance', 'dandy', 'dared',
            'dares', 'darks', 'darns', 'darts', 'dated', 'dates', 'datum', 'daubs', 'daunt', 'dawns',
            'deals', 'dealt', 'death', 'debit', 'debts', 'debug', 'debut', 'decal', 'decay', 'decks',
            'decor', 'decoy', 'decry', 'deeds', 'deems', 'deeps', 'deers', 'defer', 'deify', 'deign',
            'deity', 'delay', 'delta', 'delve', 'demon', 'demur', 'denim', 'dense', 'depot', 'depth',
            'derby', 'desks', 'deter', 'detox', 'deuce', 'devil', 'diary', 'dicey', 'diets', 'digit',
            'dimly', 'dined', 'diner', 'dines', 'dingo', 'dingy', 'diode', 'dirge', 'dirty', 'disco',
            'discs', 'ditch', 'ditto', 'ditty', 'divan', 'diver', 'dives', 'dizzy', 'docks', 'dodge',
            'dodgy', 'doers', 'doing', 'dolls', 'dolly', 'domed', 'domes', 'donor', 'donut', 'dooms',
            'doors', 'dopey', 'dosed', 'doses', 'dotes', 'dotty', 'dough', 'douse', 'dowdy', 'dowel',
            'downs', 'downy', 'dowry', 'dozed', 'dozen', 'dozer', 'draft', 'drags', 'drain', 'drake',
            'drama', 'drank', 'drape', 'drawl', 'drawn', 'draws', 'dread', 'dream', 'dress', 'dried',
            'drier', 'drift', 'drill', 'drink', 'drips', 'drive', 'droit', 'droll', 'drone', 'drool',
            'droop', 'drops', 'dross', 'drove', 'drown', 'drugs', 'drums', 'drunk', 'dryad', 'dryer',
            'dryly', 'ducal', 'ducks', 'ducts', 'duels', 'duets', 'duffs', 'dulls', 'dumbo', 'dummy',
            'dumps', 'dumpy', 'dunce', 'dunes', 'dunks', 'duped', 'dupes', 'dusty', 'dutch', 'dwarf',
            'dwell', 'dwelt', 'eager', 'eagle', 'early', 'earns', 'earth', 'eased', 'easel', 'eaten',
            'eater', 'eaves', 'ebbed', 'ebony', 'eclat', 'edged', 'edger', 'edges', 'edgy', 'edict',
            'edits', 'eerie', 'eight', 'eject', 'elate', 'elbow', 'elder', 'elect', 'elfin', 'elide',
            'elite', 'elope', 'elude', 'elves', 'email', 'ember', 'emcee', 'emery', 'emirs', 'emits',
            'emoji', 'emote', 'empty', 'enact', 'ended', 'endow', 'enema', 'enemy', 'enjoy', 'ennui',
            'ensue', 'enter', 'entry', 'envoy', 'epoch', 'epoxy', 'equal', 'equip', 'erase', 'erode',
            'erred', 'error', 'erupt', 'essay', 'ether', 'ethic', 'ethos', 'ethyl', 'evade', 'event',
            'every', 'evict', 'evoke', 'exact', 'exalt', 'exams', 'excel', 'exert', 'exile', 'exist',
            'expat', 'expel', 'extol', 'extra', 'exude', 'exult', 'eying', 'eyrie', 'fable', 'faced',
            'faces', 'facet', 'facts', 'faded', 'fades', 'fails', 'faint', 'fairy', 'faith', 'faked',
            'faker', 'falls', 'false', 'famed', 'fancy', 'fangs', 'farce', 'farms', 'fatal', 'fates',
            'fatso', 'fatty', 'fault', 'fauna', 'favor', 'feast', 'feats', 'fecal', 'feeds', 'feels',
            'feign', 'feint', 'fella', 'felon', 'femme', 'femur', 'fence', 'fends', 'feral', 'ferns',
            'ferry', 'fetal', 'fetch', 'fetid', 'fetus', 'feuds', 'fever', 'fewer', 'fiber', 'fibre',
            'ficus', 'field', 'fiend', 'fiery', 'fifth', 'fifty', 'fight', 'filch', 'filed', 'filer',
            'files', 'filet', 'fills', 'films', 'filmy', 'filth', 'final', 'finch', 'finds', 'fined',
            'finer', 'fines', 'fired', 'fires', 'firms', 'first', 'fishy', 'fists', 'fixed', 'fixer',
            'fixes', 'fizzy', 'fjord', 'flack', 'flags', 'flair', 'flake', 'flaky', 'flame', 'flank',
            'flaps', 'flare', 'flash', 'flask', 'flats', 'flaws', 'fleas', 'fleck', 'fledge', 'flesh',
            'flick', 'flier', 'flies', 'fling', 'flint', 'flips', 'flirt', 'float', 'flock', 'flood',
            'floor', 'flops', 'flora', 'floss', 'flour', 'flout', 'flows', 'fluid', 'fluke', 'flung',
            'flunk', 'flush', 'flute', 'foams', 'foamy', 'focal', 'focus', 'foggy', 'foils', 'folds',
            'folks', 'folly', 'fonts', 'foods', 'fools', 'foray', 'force', 'forge', 'forgo', 'forks',
            'forms', 'forte', 'forth', 'forty', 'forum', 'fosse', 'fouls', 'found', 'fours', 'foxes',
            'foyer', 'frail', 'frame', 'frank', 'fraud', 'frays', 'freak', 'freed', 'fresh', 'friar',
            'fried', 'fries', 'frill', 'frisk', 'fritz', 'frizz', 'frock', 'frogs', 'frond', 'front',
            'frost', 'froth', 'frown', 'froze', 'fruit', 'frump', 'fudge', 'fuels', 'fully', 'fumes',
            'funds', 'fungi', 'funky', 'funny', 'furry', 'fused', 'fuses', 'fussy', 'fusty', 'fuzzy',
            'gaffe', 'gaily', 'gains', 'gaits', 'gales', 'galls', 'gamer', 'games', 'gamma', 'gamut',
            'gangs', 'gaped', 'gapes', 'garbs', 'gases', 'gasps', 'gates', 'gaudy', 'gauge', 'gaunt',
            'gauze', 'gavel', 'gazer', 'gazes', 'gears', 'gecko', 'geeky', 'geeks', 'genes', 'genie',
            'genre', 'genus', 'germs', 'ghost', 'ghoul', 'giant', 'giddy', 'gifts', 'gilds', 'gills',
            'gilts', 'girls', 'girly', 'girth', 'gists', 'given', 'gives', 'gizmo', 'gland', 'glare',
            'glass', 'glaze', 'gleam', 'glean', 'glees', 'glide', 'glint', 'gloat', 'globe', 'gloom',
            'glory', 'gloss', 'glove', 'glows', 'glued', 'glues', 'glyph', 'gnash', 'gnats', 'gnome',
            'goads', 'goals', 'goats', 'godly', 'goers', 'going', 'golds', 'golfs', 'golly', 'goner',
            'gonna', 'goody', 'gooey', 'goofy', 'goose', 'gorge', 'gotta', 'gouge', 'gourd', 'gowns',
            'grace', 'grade', 'grads', 'graft', 'grail', 'grain', 'grams', 'grand', 'grant', 'grape',
            'graph', 'grasp', 'grass', 'grate', 'grave', 'gravy', 'grays', 'graze', 'great', 'greed',
            'green', 'greet', 'greys', 'grief', 'grill', 'grime', 'grimy', 'grind', 'grins', 'gripe',
            'grips', 'groan', 'groat', 'groin', 'groom', 'grope', 'gross', 'group', 'grout', 'grove',
            'growl', 'grown', 'grows', 'grubs', 'gruel', 'gruff', 'grump', 'grunt', 'guano', 'guava',
            'guard', 'guava', 'guess', 'guest', 'guide', 'guild', 'guilt', 'guise', 'gulch', 'gulls',
            'gully', 'gulps', 'gumbo', 'gummy', 'gumps', 'gunky', 'guppy', 'gusto', 'gusty', 'gypsy',
            'habit', 'hacks', 'haiku', 'hails', 'hairs', 'hairy', 'halal', 'hales', 'halls', 'halos',
            'halts', 'halve', 'hands', 'handy', 'hangs', 'happy', 'hardy', 'harem', 'harms', 'harps',
            'harsh', 'hasps', 'haste', 'hasty', 'hatch', 'hated', 'hater', 'hates', 'hauls', 'haunt',
            'haven', 'havoc', 'hawks', 'hazel', 'heads', 'heady', 'heals', 'heaps', 'heard', 'hears',
            'heart', 'heats', 'heave', 'heavy', 'hedge', 'heeds', 'heels', 'hefty', 'heirs', 'heist',
            'helix', 'hello', 'helps', 'hence', 'henna', 'herbs', 'herds', 'heron', 'hertz', 'hills',
            'hilly', 'hilts', 'hinds', 'hinge', 'hints', 'hippo', 'hippy', 'hired', 'hitch', 'hives',
            'hoard', 'hobby', 'hoist', 'holds', 'holes', 'holly', 'holms', 'homer', 'homes', 'honey',
            'honks', 'honor', 'hoods', 'hoody', 'hoofs', 'hooks', 'hoops', 'hoped', 'hopes', 'horns',
            'horny', 'horse', 'hosts', 'hotel', 'hotly', 'hound', 'hours', 'house', 'hover', 'howdy',
            'howls', 'hubby', 'huffs', 'huffy', 'huger', 'hulks', 'hulky', 'human', 'humid', 'humor',
            'humps', 'humpy', 'humus', 'hunks', 'hunky', 'hunts', 'hurls', 'hurry', 'hurts', 'husky',
            'husks', 'hutch', 'hydro', 'hyena', 'hymns', 'hyper', 'icier', 'icily', 'icing', 'ideal',
            'ideas', 'idiom', 'idiot', 'idled', 'idler', 'idyll', 'igloo', 'iliac', 'image', 'imbue',
            'impel', 'imply', 'inane', 'inbox', 'incur', 'index', 'indie', 'inept', 'inert', 'infer',
            'infix', 'infra', 'inked', 'inlet', 'inner', 'input', 'inter', 'intro', 'ionic', 'irate',
            'irked', 'irony', 'issue', 'itchy', 'ivory', 'jacks', 'jaded', 'jails', 'jakes', 'jambs',
            'jaunts','jazzy', 'jeans', 'jeeps', 'jeers', 'jelly', 'jenny', 'jerks', 'jerky', 'jests',
            'jewel', 'jiffy', 'jilts', 'jimmy', 'jived', 'joeys', 'joins', 'joint', 'joker', 'jokes',
            'jolly', 'jolts', 'joust', 'joyed', 'judge', 'juice', 'juicy', 'julep', 'jumbo', 'jumps',
            'jumpy', 'junco', 'juror', 'jutes', 'kabob', 'karst', 'kayak', 'kebab', 'keels', 'keens',
            'keeps', 'khaki', 'kicks', 'kills', 'kilns', 'kilts', 'kinds', 'kings', 'kiosk', 'kites',
            'knack', 'knave', 'knead', 'kneel', 'knees', 'knelt', 'knife', 'knits', 'knobs', 'knock',
            'knoll', 'knots', 'known', 'knows', 'koala', 'kraft', 'kudos', 'label', 'labor', 'laced',
            'laces', 'lacks', 'laden', 'ladle', 'lager', 'lairs', 'lakes', 'lambs', 'lamed', 'lamer',
            'lamps', 'lance', 'lands', 'lanes', 'lanky', 'lapel', 'lapse', 'large', 'largo', 'larks',
            'larva', 'laser', 'lasso', 'lasts', 'latch', 'later', 'latex', 'lathe', 'latte', 'lauds',
            'laugh', 'lawns', 'layer', 'leads', 'leafy', 'leaks', 'leaky', 'leans', 'leaps', 'leapt',
            'learn', 'lease', 'leash', 'least', 'leave', 'ledge', 'leech', 'leeks', 'lefts', 'lefty',
            'legal', 'leggy', 'lemma', 'lemon', 'lemur', 'lends', 'level', 'lever', 'libel', 'licks',
            'lifts', 'light', 'liked', 'liken', 'likes', 'lilac', 'lilts', 'limbo', 'limbs', 'limed',
            'limes', 'limit', 'limps', 'lined', 'linen', 'liner', 'lines', 'lingo', 'links', 'lions',
            'lipid', 'lists', 'liter', 'lithe', 'lived', 'liven', 'liver', 'lives', 'livid', 'llama',
            'loads', 'loafs', 'loams', 'loamy', 'loans', 'lobby', 'lobed', 'lobes', 'local', 'locks',
            'locus', 'lodge', 'lofts', 'lofty', 'logic', 'logos', 'loins', 'looks', 'looms', 'loons',
            'loony', 'loops', 'loopy', 'loose', 'loots', 'lords', 'lorry', 'loser', 'loses', 'lossy',
            'lousy', 'loved', 'lover', 'loves', 'lower', 'lowly', 'loyal', 'lucid', 'lucky', 'lumps',
            'lumpy', 'lunar', 'lunch', 'lunge', 'lungs', 'lurch', 'lured', 'lures', 'lurks', 'lusty',
            'lymph', 'lynch', 'lyric', 'macaw', 'maces', 'macho', 'macro', 'madam', 'madly', 'mafia',
            'magic', 'magma', 'mails', 'maims', 'major', 'maker', 'makes', 'males', 'malls', 'malts',
            'malty', 'mamba', 'manga', 'mange', 'mango', 'mania', 'manic', 'manor', 'maple', 'march',
            'mares', 'marks', 'marsh', 'masks', 'mason', 'match', 'mated', 'mates', 'mauve', 'maxim',
            'mayor', 'mazes', 'mealy', 'meals', 'means', 'meant', 'meats', 'meaty', 'media', 'medic',
            'meets', 'melee', 'melon', 'melts', 'memos', 'mends', 'menus', 'mercy', 'merge', 'merit',
            'merry', 'messy', 'metal', 'meter', 'metre', 'metro', 'micro', 'midst', 'might', 'miles',
            'milks', 'milky', 'mills', 'mimic', 'mince', 'minds', 'mined', 'miner', 'mines', 'minor',
            'mints', 'minus', 'mired', 'mirth', 'miser', 'misty', 'miter', 'mites', 'mitre', 'mitts',
            'mixed', 'mixer', 'moans', 'moats', 'mocks', 'model', 'modem', 'modes', 'mogul', 'moist',
            'molal', 'molar', 'molds', 'moldy', 'moles', 'molls', 'mommy', 'money', 'monks', 'month',
            'moods', 'moody', 'moons', 'moose', 'moral', 'morel', 'moron', 'morph', 'mossy', 'motel',
            'moths', 'motif', 'motor', 'motto', 'moult', 'mound', 'mount', 'mourn', 'mouse', 'mousy',
            'mouth', 'moved', 'mover', 'moves', 'movie', 'mowed', 'mower', 'moxie', 'mucus', 'muddy',
            'muffs', 'mufti', 'muggy', 'mulch', 'mules', 'mulls', 'mummy', 'mumps', 'mural', 'murky',
            'mushy', 'music', 'musky', 'musty', 'muted', 'mutes', 'myrrh', 'myths', 'nadir', 'nails',
            'naive', 'naked', 'named', 'names', 'nanny', 'napes', 'nappy', 'narco', 'nasal', 'nasty',
            'natal', 'naval', 'navel', 'neaps', 'necks', 'needs', 'needy', 'nerve', 'nervy', 'nests',
            'never', 'newer', 'newly', 'newts', 'nexus', 'niche', 'nicks', 'niece', 'night', 'ninja',
            'ninth', 'nitro', 'noble', 'nobly', 'nodel', 'nodes', 'noise', 'noisy', 'nomad', 'nooks',
            'norms', 'north', 'nosed', 'nosey', 'notch', 'noted', 'notes', 'novel', 'nudge', 'nulls',
            'numbs', 'nurse', 'nutty', 'nylon', 'nymph', 'oaken', 'oasis', 'occur', 'ocean', 'octyl',
            'oddly', 'odors', 'offal', 'offer', 'often', 'oiled', 'oinks', 'olive', 'omega', 'onset',
            'oohed', 'oomph', 'oozed', 'oozes', 'opens', 'opera', 'opted', 'optic', 'orbit', 'order',
            'organ', 'osier', 'other', 'otter', 'ought', 'ounce', 'outer', 'outdo', 'outgo', 'ovary',
            'ovens', 'overt', 'owned', 'owner', 'oxide', 'ozone', 'paced', 'pacer', 'paces', 'packs',
            'paddy', 'pagan', 'paged', 'pager', 'pages', 'pails', 'pains', 'paint', 'pairs', 'paler',
            'pales', 'palms', 'palsy', 'panda', 'panel', 'panes', 'pangs', 'panic', 'pansy', 'pants',
            'papal', 'paper', 'parks', 'parry', 'parse', 'parts', 'party', 'pasta', 'paste', 'pasty',
            'patch', 'paths', 'patio', 'patsy', 'patty', 'pause', 'paved', 'paver', 'paves', 'pawed',
            'payer', 'peace', 'peach', 'peaks', 'pearl', 'pears', 'pecan', 'pecks', 'pedal', 'peeks',
            'peels', 'peers', 'penal', 'pence', 'pends', 'penny', 'perch', 'peril', 'perks', 'perky',
            'perms', 'pesky', 'pesto', 'petal', 'peter', 'petty', 'phase', 'phone', 'photo', 'piano',
            'picks', 'picky', 'piece', 'piers', 'pigmy', 'piked', 'piled', 'piles', 'pills', 'pilot',
            'pinch', 'pined', 'pines', 'pints', 'piper', 'pipes', 'pique', 'pitch', 'piths', 'pithy',
            'piton', 'pitas', 'pivot', 'pixel', 'pixie', 'pizza', 'place', 'plaid', 'plain', 'plane',
            'plank', 'plans', 'plant', 'plate', 'playa', 'plays', 'plaza', 'plead', 'pleas', 'pleat',
            'plied', 'plier', 'plies', 'plods', 'plonk', 'plops', 'plots', 'plows', 'ploys', 'pluck',
            'plugs', 'plumb', 'plume', 'plump', 'plums', 'plunk', 'plush', 'poems', 'poets', 'point',
            'poise', 'poked', 'poker', 'pokes', 'polar', 'poles', 'polka', 'polls', 'polyp', 'ponds',
            'pools', 'popes', 'poppy', 'porch', 'pored', 'pores', 'porky', 'ports', 'posed', 'poser',
            'poses', 'posit', 'posse', 'posts', 'potty', 'pouch', 'pouty', 'power', 'prams', 'prank',
            'prawn', 'prays', 'preen', 'press', 'preys', 'price', 'prick', 'pride', 'pried', 'prime',
            'primp', 'print', 'prior', 'prism', 'privy', 'prize', 'probe', 'prods', 'proem', 'promo',
            'prone', 'prong', 'proof', 'props', 'prose', 'proud', 'prove', 'prowl', 'proxy', 'prude',
            'prune', 'psalm', 'pubic', 'pudgy', 'puffs', 'puffy', 'pulls', 'pulps', 'pulse', 'pumps',
            'punch', 'pupal', 'pupil', 'puppy', 'puree', 'purge', 'purrs', 'purse', 'pushy', 'putts',
            'putty', 'pygmy', 'pylon', 'quack', 'quaff', 'quail', 'qualm', 'quark', 'quart', 'queen',
            'queer', 'query', 'quest', 'queue', 'quick', 'quiet', 'quill', 'quilt', 'quirk', 'quota',
            'quote', 'quoth', 'rabbi', 'rabid', 'raced', 'racer', 'races', 'racks', 'radar', 'radii',
            'radio', 'radon', 'rafts', 'raged', 'rages', 'raids', 'rails', 'rains', 'rainy', 'raise',
            'rally', 'ramps', 'ranch', 'randy', 'range', 'ranks', 'rants', 'rapid', 'rated', 'rates',
            'ratio', 'raved', 'raven', 'raves', 'rayon', 'razor', 'reach', 'reads', 'ready', 'realm',
            'reams', 'reaps', 'rebel', 'rebus', 'rebut', 'recap', 'recur', 'reeds', 'reedy', 'reefs',
            'reeks', 'reels', 'regal', 'reign', 'reins', 'relax', 'relay', 'relic', 'remit', 'renal',
            'renew', 'rents', 'repay', 'repel', 'reply', 'rerun', 'reset', 'resin', 'rests', 'retro',
            'retry', 'revel', 'rider', 'rides', 'ridge', 'rifle', 'rifts', 'rigid', 'rigor', 'riled',
            'rills', 'rinds', 'rings', 'rinse', 'riots', 'ripen', 'riper', 'risen', 'riser', 'rises',
            'risks', 'risky', 'rites', 'ritzy', 'rival', 'riven', 'river', 'rivet', 'roads', 'roams',
            'roars', 'roast', 'robed', 'robes', 'robin', 'robot', 'rocks', 'rocky', 'roger', 'rogue',
            'roles', 'rolls', 'roman', 'roofs', 'rooms', 'roomy', 'roost', 'roots', 'roped', 'ropes',
            'roses', 'rotor', 'rouge', 'rough', 'round', 'rouse', 'route', 'rover', 'rowdy', 'rowed',
            'rower', 'royal', 'rugby', 'ruins', 'ruled', 'ruler', 'rules', 'rumba', 'rumor', 'rupee',
            'rural', 'rusty', 'saber', 'sable', 'sabre', 'sadly', 'safes', 'safer', 'saint', 'sakes',
            'salad', 'sales', 'sally', 'salon', 'salsa', 'salts', 'salty', 'salve', 'salvo', 'sands',
            'sandy', 'saner', 'sappy', 'satin', 'satyr', 'sauce', 'saucy', 'sauna', 'savor', 'savvy',
            'scale', 'scalp', 'scaly', 'scamp', 'scams', 'scant', 'scare', 'scarf', 'scary', 'scene',
            'scent', 'scoff', 'scold', 'scone', 'scoop', 'scoot', 'scope', 'scops', 'score', 'scorn',
            'scout', 'scowl', 'scram', 'scrap', 'scree', 'screw', 'scrub', 'scrum', 'seals', 'seams',
            'seats', 'sedan', 'seeds', 'seedy', 'seeks', 'seems', 'seeps', 'seize', 'semen', 'sense',
            'sepia', 'serif', 'serve', 'setup', 'seven', 'sever', 'shade', 'shady', 'shaft', 'shake',
            'shaky', 'shale', 'shall', 'shame', 'shape', 'shard', 'share', 'shark', 'sharp', 'shave',
            'shawl', 'shear', 'sheen', 'sheep', 'sheer', 'sheet', 'shelf', 'shell', 'shift', 'shied',
            'shier', 'shies', 'shily', 'shine', 'shins', 'shiny', 'ships', 'shire', 'shirk', 'shirt',
            'shoal', 'shock', 'shoed', 'shoes', 'shone', 'shook', 'shoot', 'shops', 'shore', 'shorn',
            'short', 'shots', 'shout', 'shove', 'shown', 'shows', 'showy', 'shrub', 'shrug', 'shuck',
            'shunt', 'sides', 'siege', 'sieve', 'sighs', 'sight', 'sigma', 'signs', 'silks', 'silky',
            'sills', 'silly', 'silts', 'since', 'sinew', 'singe', 'sinks', 'sinus', 'siren', 'sites',
            'sixth', 'sixty', 'sized', 'sizer', 'sizes', 'skate', 'skein', 'skids', 'skied', 'skier',
            'skies', 'skill', 'skimp', 'skins', 'skips', 'skirt', 'skull', 'skunk', 'slabs', 'slack',
            'slain', 'slang', 'slant', 'slaps', 'slash', 'slate', 'slats', 'sleek', 'sleep', 'sleet',
            'slept', 'slice', 'slick', 'slide', 'slime', 'slimy', 'sling', 'slink', 'slope', 'slops',
            'slots', 'sloth', 'slows', 'slugs', 'slump', 'slums', 'slung', 'slunk', 'slurp', 'slurs',
            'smack', 'small', 'smart', 'smash', 'smear', 'smell', 'smelt', 'smile', 'smirk', 'smite',
            'smith', 'smock', 'smoke', 'smoky', 'snack', 'snafu', 'snags', 'snail', 'snake', 'snaps',
            'snare', 'snarl', 'sneak', 'sneer', 'snide', 'sniff', 'snips', 'snobs', 'snoop', 'snore',
            'snort', 'snout', 'snowy', 'snubs', 'snuck', 'snuff', 'soapy', 'soars', 'sober', 'socks',
            'softy', 'soggy', 'soils', 'solar', 'solid', 'solos', 'solve', 'sonar', 'songs', 'sonic',
            'sooth', 'sooty', 'soppy', 'sorry', 'sorts', 'souls', 'sound', 'south', 'space', 'spade',
            'spans', 'spare', 'spark', 'spasm', 'spawn', 'speak', 'spear', 'speck', 'specs', 'speed',
            'spell', 'spelt', 'spend', 'spent', 'spice', 'spicy', 'spied', 'spiel', 'spies', 'spike',
            'spiky', 'spill', 'spine', 'spiny', 'spite', 'split', 'spoil', 'spoke', 'spoof', 'spook',
            'spool', 'spoon', 'spore', 'sport', 'spots', 'spout', 'spray', 'spree', 'sprig', 'spurn',
            'spurs', 'spurt', 'squad', 'squat', 'squid', 'stabs', 'stack', 'staff', 'stage', 'stags',
            'staid', 'stain', 'stair', 'stake', 'stale', 'stalk', 'stall', 'stamp', 'stand', 'stank',
            'staph', 'stare', 'stark', 'stars', 'start', 'stash', 'state', 'stays', 'steak', 'steal',
            'steam', 'steed', 'steel', 'steep', 'steer', 'stems', 'steps', 'stern', 'stews', 'stick',
            'stiff', 'still', 'stilt', 'sting', 'stink', 'stint', 'stock', 'stoic', 'stoke', 'stole',
            'stomp', 'stone', 'stony', 'stood', 'stool', 'stoop', 'stops', 'store', 'stork', 'storm',
            'story', 'stout', 'stove', 'straw', 'stray', 'strip', 'strew', 'stuck', 'studs', 'study',
            'stuff', 'stump', 'stung', 'stunk', 'stunt', 'style', 'suave', 'suing', 'suite', 'suits',
            'sulks', 'sulky', 'sumac', 'sunny', 'super', 'surge', 'surly', 'sushi', 'swabs', 'swami',
            'swamp', 'swams', 'swank', 'swans', 'swaps', 'swarm', 'swath', 'swear', 'sweat', 'sweep',
            'sweet', 'swell', 'swept', 'swift', 'swill', 'swims', 'swine', 'swing', 'swipe', 'swirl',
            'swish', 'swoon', 'swoop', 'sword', 'swore', 'sworn', 'swung', 'synod', 'syrup', 'tabby',
            'table', 'taboo', 'tacit', 'tacks', 'tacky', 'taffy', 'tails', 'taint', 'taken', 'taker',
            'takes', 'tales', 'talks', 'talon', 'tamed', 'tamer', 'tango', 'tangs', 'tangy', 'tanks',
            'taper', 'tapes', 'tapir', 'tardy', 'tasks', 'taste', 'tasty', 'taunt', 'tawny', 'taxes',
            'teach', 'teams', 'tears', 'tease', 'teddy', 'teens', 'teeth', 'tempo', 'temps', 'tenet',
            'tenor', 'tense', 'tenth', 'tents', 'tepee', 'tepid', 'terms', 'terns', 'tests', 'texts',
            'thank', 'theft', 'their', 'theme', 'there', 'these', 'theta', 'thick', 'thief', 'thigh',
            'thing', 'think', 'third', 'thong', 'thorn', 'those', 'three', 'threw', 'throw', 'throe',
            'thuds', 'thugs', 'thumb', 'thump', 'tiara', 'tidal', 'tided', 'tides', 'tiers', 'tiger',
            'tight', 'tiled', 'tiles', 'tilts', 'timid', 'times', 'tined', 'tines', 'tinge', 'tints',
            'tipsy', 'tired', 'titan', 'title', 'toast', 'toddy', 'today', 'token', 'tolls', 'tombs',
            'tonal', 'toned', 'toner', 'tones', 'tongs', 'tonic', 'tools', 'tooth', 'topaz', 'topic',
            'torch', 'torso', 'total', 'totem', 'touch', 'tough', 'tours', 'towel', 'tower', 'towns',
            'toxic', 'toxin', 'trace', 'track', 'tract', 'trade', 'trail', 'train', 'trait', 'tramp',
            'traps', 'trash', 'trawl', 'trays', 'tread', 'treat', 'treed', 'trees', 'treks', 'trend',
            'triad', 'trial', 'tribe', 'trice', 'trick', 'tried', 'trier', 'tries', 'trill', 'trims',
            'tripe', 'trite', 'troll', 'troop', 'trope', 'troth', 'trots', 'trout', 'truce', 'truck',
            'truly', 'trump', 'trunk', 'truss', 'trust', 'truth', 'tryst', 'tubal', 'tubes', 'tucks',
            'tulip', 'tumor', 'tuned', 'tuner', 'tunes', 'tunic', 'turbo', 'turfs', 'turns', 'tusks',
            'tutor', 'twang', 'tweak', 'tweed', 'tweet', 'twerp', 'twice', 'twigs', 'twill', 'twine',
            'twins', 'twirl', 'twist', 'tying', 'typed', 'types', 'udder', 'ulcer', 'ultra', 'umbra',
            'umped', 'uncle', 'uncut', 'under', 'undid', 'undue', 'unfit', 'unify', 'union', 'unite',
            'units', 'unity', 'unlit', 'unmet', 'until', 'untie', 'unwed', 'unzip', 'upper', 'upset',
            'urban', 'urged', 'urges', 'urine', 'usage', 'usher', 'using', 'usurp', 'usual', 'utter',
            'uvula', 'vague', 'valet', 'valid', 'valor', 'value', 'valve', 'vamps', 'vanes', 'vapid',
            'vapor', 'vault', 'vaunt', 'vegan', 'veils', 'veins', 'veldt', 'venal', 'venom', 'venue',
            'verbs', 'verge', 'verse', 'verso', 'video', 'views', 'vigor', 'viler', 'villa', 'vinca',
            'vined', 'vines', 'vinyl', 'viola', 'viper', 'viral', 'virus', 'visor', 'visit', 'vista',
            'vital', 'vivid', 'vixen', 'vizor', 'vocal', 'vodka', 'vogue', 'voice', 'voila', 'volts',
            'voted', 'voter', 'votes', 'vouch', 'vowed', 'vowel', 'vying', 'wacky', 'waded', 'wader',
            'wades', 'wafer', 'waged', 'wager', 'wages', 'wagon', 'waifs', 'wails', 'waist', 'waits',
            'waked', 'waken', 'wakes', 'walks', 'walls', 'waltz', 'wands', 'wanes', 'wants', 'wards',
            'wares', 'warms', 'warns', 'warps', 'warts', 'warty', 'waste', 'watch', 'water', 'watts',
            'waved', 'waver', 'waves', 'waxed', 'waxen', 'weals', 'weans', 'wears', 'weary', 'weave',
            'wedge', 'weeds', 'weedy', 'weeks', 'weeps', 'weigh', 'weird', 'wells', 'wench', 'whale',
            'whack', 'wheat', 'wheel', 'where', 'which', 'while', 'whims', 'whine', 'whiny', 'whips',
            'whirl', 'whisk', 'white', 'whole', 'whoop', 'whose', 'widen', 'wider', 'widow', 'width',
            'wield', 'wilds', 'wiles', 'wills', 'wimps', 'wimpy', 'wince', 'winch', 'winds', 'windy',
            'wined', 'wines', 'wings', 'winks', 'wiper', 'wired', 'wires', 'wiser', 'witch', 'withe',
            'witty', 'wives', 'woken', 'woman', 'women', 'woods', 'woody', 'wooer', 'wools', 'wooly',
            'woozy', 'words', 'wordy', 'works', 'world', 'worms', 'worry', 'worse', 'worst', 'worth',
            'would', 'wound', 'wrack', 'wraps', 'wrath', 'wreak', 'wreck', 'wrest', 'wring', 'wrist',
            'write', 'wrong', 'wrote', 'wrung', 'xenon', 'xerox', 'yacht', 'yanks', 'yards', 'yarns',
            'yearn', 'years', 'yeast', 'yells', 'yield', 'yodel', 'yokel', 'yolks', 'young', 'yours',
            'youth', 'yucca', 'yummy', 'zappy', 'zebra', 'zesty', 'zilch', 'zincs', 'zingy', 'zippy',
            'zloty', 'zonal', 'zones', 'zooms',
            'abaci', 'aback', 'abaft', 'abase', 'abash', 'abate', 'abbey', 'abbot', 'abhor', 'ablow',
            'abuzz', 'acmes', 'acned', 'actin', 'addon', 'addle', 'adieu', 'adios', 'admin', 'affix',
            'afoul', 'agape', 'agave', 'aglow', 'ahold', 'aimed', 'aimer', 'aired', 'aitch', 'aland',
            'alder', 'alias', 'aline', 'allay', 'aloof', 'aloud', 'altar', 'amble', 'amiss', 'amour',
            'angst', 'anime', 'anion', 'anise', 'aping', 'apnea', 'aptly', 'armor', 'arose', 'arson',
            'ashes', 'atlas', 'atoll', 'atone', 'auger', 'aunts', 'aunty', 'avast', 'awash', 'babel',
            'backs', 'baits', 'baked', 'bakes', 'balks', 'balky', 'balls', 'balms', 'banes', 'bangs',
            'banks', 'barbs', 'bards', 'bared', 'bares', 'barks', 'barmy', 'barns', 'baron', 'barre',
            'based', 'basil', 'basis', 'baste', 'batch', 'bated', 'bathe', 'baths', 'batty', 'baulk',
            'bawls', 'beaks', 'beams', 'beano', 'beans', 'bears', 'beats', 'beaus', 'beaut', 'beaux',
            'bebop', 'bedew', 'beech', 'beefs', 'beefy', 'beeps', 'beers', 'beery', 'beets', 'began',
            'beget', 'begot', 'beige', 'belie', 'bells', 'belts', 'bends', 'bendy', 'bergs', 'bible',
            'bicep', 'bided', 'bikes', 'bills', 'bimbo', 'binds', 'bingo', 'biome', 'bipod', 'birds',
            'biter', 'bites', 'bitsy', 'blare', 'blobs', 'blocs', 'blond', 'blows', 'blurb', 'blurs',
            'boars', 'boats', 'boded', 'boils', 'bolls', 'bombs', 'boned', 'bonks', 'booby', 'booms',
            'boons', 'booty', 'booze', 'borer', 'bores', 'borne', 'boron', 'bosom', 'bossy', 'boule',
            'bouts', 'bowed', 'boxed', 'boxes', 'brace', 'bract', 'brags', 'brake', 'brass', 'bravo',
            'brays', 'breed', 'brine', 'brows', 'bucks', 'buddy', 'buffs', 'bugle', 'bulbs', 'bulge',
            'bulks', 'bulls', 'bumps', 'bunks', 'bunts', 'buoys', 'burns', 'burps', 'busby', 'buses',
            'bushy', 'busts', 'bytes', 'cadge', 'caged', 'cages', 'caked', 'cakes', 'calls', 'calms',
            'camps', 'canes', 'canid', 'canto', 'cants', 'capes', 'capon', 'cards', 'cared', 'carer',
            'cares', 'carob', 'carts', 'cases', 'casts', 'caves', 'cells', 'cents', 'chaps', 'chick',
            'chins', 'chips', 'chomp', 'chops', 'circa', 'cisco', 'cited', 'cites', 'clams', 'clank',
            'clans', 'claps', 'claws', 'clays', 'clips', 'clods', 'clogs', 'clout', 'clubs', 'clues',
            'clunk', 'coals', 'coats', 'coded', 'codes', 'coils', 'coins', 'colas', 'color', 'colts',
            'comer', 'comes', 'comma', 'cones', 'conte', 'cooed', 'cools', 'coops', 'coord', 'copes',
            'copse', 'corgi', 'corns', 'coups', 'cowed', 'cozen', 'crags', 'craps', 'credo', 'creed',
            'creme', 'crept', 'cried', 'crier', 'cries', 'crimp', 'croft', 'crony', 'cubes', 'culls',
            'cures', 'curve', 'cynic', 'dared', 'dares', 'darks', 'darns', 'daubs', 'dawns', 'debit',
        ]

        def parse_plain(text):
            words = []
            for line in text.strip().splitlines():
                w = line.strip().lower()
                if len(w) == 5 and w.isalpha():
                    words.append(w)
            return words

        def parse_tuple_format(text):
            import re
            words = []
            for match in re.finditer(r'\(([a-zA-Z]+),', text):
                w = match.group(1).strip().lower()
                if len(w) == 5 and w.isalpha():
                    words.append(w)
            return words

        async def load_words():
            if self.words_cache is not None:
                return self.words_cache
            all_filtered = {w for w in self.BUILTIN_WORDS if len(w) == 5 and w.isalpha()}
            parsers = [parse_plain, parse_tuple_format, parse_plain]
            async with aiohttp.ClientSession() as session:
                for url, parser in zip(self.WORDS_URLS, parsers):
                    try:
                        async with session.get(url) as resp:
                            if resp.status == 200:
                                text = await resp.text()
                                all_filtered.update(parser(text))
                    except Exception:
                        pass
            if not all_filtered:
                return None
            filtered = list(all_filtered)
            random.shuffle(filtered)
            self.words_cache = filtered
            return self.words_cache

        async def check_username(username):
            from telethon.tl import functions
            try:
                result = await client(functions.account.CheckUsernameRequest(username=username))
                return result
            except Exception:
                return False

        async def pusername_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}pusername'):
                return

            parts = event.text.split()
            count = 5
            if len(parts) >= 2:
                try:
                    count = int(parts[1])
                except ValueError:
                    await event.edit(
                        f'**🔍 Username Finder**\n\n'
                        f'❌ Неверный формат!\n'
                        f'Использование: `{self.prefix}pusername <количество>`'
                    )
                    return

            if count < 1 or count > 50:
                await event.edit(
                    '**🔍 Username Finder**\n\n'
                    '❌ Количество должно быть от 1 до 50'
                )
                return

            await event.edit(
                '**🔍 Username Finder**\n\n'
                '⏳ Загрузка словарей (3 источника)...'
            )

            words = await load_words()
            if not words:
                await event.edit(
                    '**🔍 Username Finder**\n\n'
                    '❌ Не удалось загрузить словарь'
                )
                return

            await event.edit(
                f'**🔍 Username Finder**\n\n'
                f'📖 Словари загружены: **{len(words)}** слов (5 букв)\n'
                f'🔎 Ищу **{count}** свободных юзернеймов...\n\n'
                f'⏳ Это может занять некоторое время...'
            )

            found = []
            checked = 0
            skipped = 0

            random.shuffle(words)

            for word in words:
                if len(found) >= count:
                    break

                username = word
                checked += 1

                try:
                    is_free = await check_username(username)
                except Exception:
                    is_free = False

                if is_free:
                    found.append(username)

                    progress_text = (
                        f'**🔍 Username Finder**\n\n'
                        f'📊 Прогресс: **{len(found)}/{count}**\n'
                        f'🔎 Проверено: **{checked}** | Занято: **{checked - len(found)}**\n\n'
                        f'**✅ Найденные юзернеймы:**\n'
                    )
                    for i, u in enumerate(found, 1):
                        progress_text += f'  {i}. @{u} — `t.me/{u}`\n'

                    if len(found) < count:
                        progress_text += f'\n⏳ Продолжаю поиск...'

                    try:
                        await event.edit(progress_text)
                    except Exception:
                        pass
                else:
                    skipped += 1

                if checked % 30 == 0 and len(found) < count:
                    try:
                        await event.edit(
                            f'**🔍 Username Finder**\n\n'
                            f'📊 Прогресс: **{len(found)}/{count}**\n'
                            f'🔎 Проверено: **{checked}** | Занято: **{skipped}**\n\n'
                            + (
                                '**✅ Найденные:**\n' +
                                ''.join(f'  {i}. @{u}\n' for i, u in enumerate(found, 1))
                                if found else ''
                            ) +
                            '\n⏳ Продолжаю поиск...'
                        )
                    except Exception:
                        pass

                await asyncio.sleep(0.5)

            if found:
                result_text = (
                    f'**🔍 Username Finder — Результат**\n\n'
                    f'📊 Проверено: **{checked}** юзернеймов\n'
                    f'✅ Свободных: **{len(found)}** | ❌ Занятых: **{skipped}**\n\n'
                    f'**🎯 Свободные юзернеймы:**\n'
                )
                for i, u in enumerate(found, 1):
                    result_text += f'  {i}. @{u} — `t.me/{u}`\n'
                result_text += f'\n💡 Занять юзернейм: **Настройки Telegram → Имя пользователя**'
            else:
                result_text = (
                    f'**🔍 Username Finder**\n\n'
                    f'📊 Проверено: **{checked}** юзернеймов\n'
                    f'😔 Свободных юзернеймов не найдено\n\n'
                    f'💡 Попробуйте ещё раз — слова выбираются случайно'
                )

            await event.edit(result_text)

        client.add_event_handler(pusername_handler, events.NewMessage(outgoing=True))
