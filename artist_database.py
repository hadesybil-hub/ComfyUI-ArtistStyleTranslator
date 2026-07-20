"""Built-in structured style profiles for observable visual traits."""

from copy import deepcopy
import unicodedata


STYLE_PROFILE_FIELDS = (
    "medium",
    "genre",
    "subject_focus",
    "linework",
    "shape_language",
    "facial_design",
    "anatomy",
    "rendering",
    "shading",
    "coloring",
    "palette",
    "lighting",
    "composition",
    "environment",
    "clothing",
    "mood",
    "detail_emphasis",
)


def _phrases(value):
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(part.strip() for part in value.split(";") if part.strip())
    return tuple(str(part).strip() for part in value if str(part).strip())


def _record(canonical_name, aliases, *profile_values):
    if len(profile_values) != len(STYLE_PROFILE_FIELDS):
        raise ValueError("Style profile field count does not match schema")
    return {
        "canonical_name": canonical_name,
        "aliases": tuple(aliases),
        "style_profile": {
            field: _phrases(value)
            for field, value in zip(STYLE_PROFILE_FIELDS, profile_values)
        },
    }


ARTISTS = (
    _record(
        "Yaegashi Nan", ("YaegashiNan", "Yaegashi-Nan"),
        "anime character illustration", "mature character portraiture", "expressive character portraits; full-body figures",
        "clean delicate linework; tapered contours", "elegant flowing shapes", "refined facial features; expressive almond-shaped eyes",
        "graceful elongated proportions", "smooth polished rendering; carefully finished surfaces", "soft cel shading; controlled tonal transitions",
        "smooth skin tones; nuanced fabric colors", "warm controlled palette; restrained accents", "warm soft illumination; subtle rim light",
        "balanced character-centered framing; clear focal hierarchy", "minimal atmospheric backdrop", "detailed clothing folds; elegant fitted garments",
        "composed; gently expressive", "faces; eyes; fabric folds; hair strands",
    ),
    _record(
        "Tony Taka", ("Tony", "TonyTaka", "Tony-Taka"),
        "polished anime illustration", "romantic fantasy", "graceful character portraits; paired figures",
        "fine continuous contours; soft edge control", "flowing rounded silhouettes", "softly modeled faces; luminous rounded eyes",
        "slender balanced proportions", "glossy refined rendering; smooth surface finish", "gentle gradient shading; soft form modeling",
        "rich harmonious colors; luminous skin tones", "jewel tones balanced with pastels", "soft radiant lighting; delicate highlights",
        "calm symmetrical framing; layered portrait depth", "ornamental fantasy settings", "flowing fantasy costumes; decorative accessories",
        "romantic; serene", "eyes; hair; fabric; ornamental details",
    ),
    _record(
        "Kantoku", ("Kantoku-Artist",),
        "clean anime illustration", "slice-of-life", "youthful characters; everyday interactions",
        "precise lightweight linework; crisp contours", "light compact silhouettes", "delicate faces; bright readable eyes",
        "youthful natural proportions", "clean digital rendering; tidy surface detail", "light cel shading; gentle gradients",
        "fresh pastel-leaning colors", "bright airy palette; soft accent colors", "clear daylight; diffuse ambient glow",
        "spacious balanced layouts; casual scene framing", "bright interiors; open everyday spaces", "casual layered clothing; small fashion details",
        "cheerful; relaxed", "facial expressions; clothing details; everyday objects",
    ),
    _record(
        "Mika Pikazo", ("MikaPikazo", "Mika-Pikazo"),
        "graphic digital illustration", "pop fantasy", "energetic character portraits; fashion-focused figures",
        "sharp confident contours; varied graphic strokes", "angular layered shapes; bold silhouette breaks", "stylized facial geometry; intense expressive eyes",
        "dynamic fashion proportions", "high-impact graphic rendering; layered decorative surfaces", "hard-edged cel shading; abrupt color transitions",
        "high-saturation color blocking; vivid accents", "electric complementary palette; multicolor contrasts", "bright punchy illumination; graphic highlights",
        "dynamic poster framing; dense asymmetric balance", "abstract decorative backdrops; layered symbols", "fashion-forward costumes; graphic accessories",
        "energetic; playful", "eyes; color blocks; accessories; decorative shapes",
    ),
    _record(
        "lack", ("Lack", "lackartist"),
        "polished digital character illustration; crisp fantasy portrait art", "ornamental dark fantasy", "commanding character portraits; design-focused fantasy figures",
        "controlled angular linework; crisp selective edge accents", "strong tapered silhouettes; intricate ornamental geometry", "defined facial planes; focused jewel-like eyes",
        "athletic heroic proportions; poised stance", "high-clarity dimensional rendering; meticulously separated materials", "firm planar shading; deep sculpted shadows",
        "deep chromatic fields; selective vivid accents", "dark jewel palette; concentrated warm highlights", "focused theatrical lighting; narrow luminous rim light",
        "iconic centered portrait composition; layered character depth", "abstract dark fantasy atmosphere; restrained background motifs", "ornate layered fantasy costumes; finely designed metal accessories",
        "intense; ceremonial", "facial focus; ornament; armor materials; silhouette edges",
    ),
    _record(
        "redjuice", ("Redjuice", "red-juice"),
        "cinematic science-fiction illustration; sleek digital concept art", "near-future visual narrative", "futuristic characters; technology-centered urban scenes",
        "fine technical linework; precise luminous edge accents", "elongated aerodynamic forms; interlocking mechanical geometry", "refined angular faces; narrow sharply lit eyes",
        "slender stylized proportions; controlled gesture", "layered atmospheric rendering; intricate synthetic surface treatment", "smooth tonal modeling; deep transparent ambient shadows",
        "cool cinematic color grading; restrained signal-color accents", "blue-gray and cyan palette; isolated luminous highlights", "moody directional lighting; electric rim glow",
        "asymmetric cinematic framing; strong foreground-to-background depth", "dense futuristic city structures; illuminated atmospheric haze", "technical garments; segmented armor and translucent panels",
        "tense; futuristic", "interface-like details; synthetic materials; haze; luminous edges",
    ),
    _record(
        "WLOP", ("wlop", "W-LOP"),
        "atmospheric digital painting; painterly fantasy illustration", "cinematic environmental fantasy", "environmental storytelling; figures within expansive fantasy worlds",
        "soft painterly edge transitions; minimally visible contours", "elegant flowing silhouettes; monumental sweeping forms", "realistic facial modeling; restrained expressions",
        "graceful proportions within large scenes", "layered atmospheric rendering; character integrated with environment", "blended tonal transitions; forms softened by atmosphere",
        "muted cinematic color grading; atmospheric depth colors", "subdued cool-warm palette; restrained jewel accents", "volumetric haze lighting; distant luminous atmosphere",
        "wide cinematic composition; character embedded in a large-scale world", "large-scale world building; mist-filled architecture", "flowing garments shaped by wind; painterly fabric",
        "dramatic; contemplative", "environmental scale; atmosphere; silhouette; narrative space",
    ),
    _record(
        "Guweiz", ("guweiz", "Gu Wei Zi"),
        "polished digital character illustration; game character concept art", "heroic fantasy concept art", "single heroic characters; costume-centered presentation",
        "clean controlled contours; precise costume detailing", "strong heroic silhouette; armor-driven shape design", "realistic anime-influenced facial design; focused expressions",
        "grounded heroic anatomy; confident stance", "polished fantasy character rendering; detailed material finish", "firm dimensional shading; defined armor planes",
        "rich controlled character colors; distinct material separation", "deep fantasy palette; focused accent colors", "dramatic character lighting; strong directional highlights",
        "heroic character presentation; full-figure concept framing", "restrained atmospheric backdrop; secondary environmental detail", "detailed armor and clothing design; layered game costume elements",
        "resolute; adventurous", "costume construction; armor; silhouette; character materials",
    ),
    _record(
        "Sakimichan", ("saki michan", "Saki-michan"),
        "semi-realistic digital painting; CG character illustration", "game promotional character art", "glamorous character portraits; anatomy-focused figures",
        "soft polished contours; clean facial edges", "sculpted body forms; curved glamorous silhouettes", "refined facial beauty; glossy expressive eyes",
        "detailed anatomy rendering; idealized proportions", "highly polished character rendering; smooth skin finish", "smooth volumetric modeling; carefully blended form shading",
        "luminous skin coloring; glossy material treatment", "rich saturated palette; warm skin-focused harmony", "strong rim lighting; glossy specular highlights",
        "character-dominant promotional framing; dramatic close composition", "minimal fantasy or studio backdrop", "form-fitting detailed costumes; reflective fabric and armor",
        "glamorous; dramatic", "facial beauty; skin; anatomy; glossy materials",
    ),
    _record(
        "Artgerm", ("art germ", "Stanley Artgerm Lau"),
        "commercial digital illustration; comic-influenced character art", "hero portraiture", "sharp character focus; iconic individual heroes",
        "clean confident linework; sharp controlled edges", "bold elegant silhouette; balanced graphic shapes", "elegant facial features; clear heroic expression",
        "idealized comic-informed anatomy; poised proportions", "clean polished rendering; premium illustration finish", "controlled smooth shading; crisp form definition",
        "controlled commercial colors; clean local color separation", "balanced graphic palette; selective vivid accents", "clean studio lighting; precise focal highlights",
        "hero portrait composition; balanced graphic composition", "minimal supporting backdrop; graphic negative space", "refined hero costumes; clearly designed accessories",
        "confident; aspirational", "face; silhouette; graphic balance; premium finish",
    ),
    _record(
        "Rella", ("rella",),
        "luminous digital illustration", "dreamlike fantasy", "ethereal character portraits; floating figures",
        "fine luminous linework; delicate broken contours", "light floating forms; translucent layers", "delicate faces; sparkling reflective eyes",
        "slender weightless proportions", "translucent layered rendering; sparkling surface effects", "soft diffused shading; glowing tonal transitions",
        "pastel gradients; iridescent accents", "pearl-like palette; cool luminous pastels", "glowing diffused light; scattered highlights",
        "airy layered composition; generous negative space", "dreamlike atmospheric spaces; floating particles", "light translucent garments; delicate ornaments",
        "ethereal; hopeful", "light effects; eyes; translucent fabric; particles",
    ),
    _record(
        "Nardack", ("nardack",),
        "polished anime illustration", "decorative fantasy", "elegant character portraits; poised figures",
        "smooth precise contours; fine decorative lines", "slender curved silhouettes", "gentle faces; glossy expressive eyes",
        "elongated graceful proportions", "smooth glossy rendering; ornamental surface finish", "soft cel gradients; subtle form shading",
        "harmonious soft colors; polished highlights", "pastel jewel palette; balanced accents", "gentle luminous lighting; soft rim glow",
        "balanced portrait framing; graceful visual flow", "decorative fantasy backdrops", "ornate costumes; delicate accessories",
        "elegant; calm", "eyes; hair; ornaments; costume trim",
    ),
    _record(
        "Anmi", ("anmi",),
        "soft anime illustration", "intimate slice-of-life", "quiet character portraits; gentle everyday moments",
        "thin understated linework; soft contours", "light graceful forms; compact silhouettes", "subtle expressions; softly defined eyes",
        "natural youthful proportions", "delicate low-contrast rendering; restrained detail", "soft ambient shading; shallow tonal range",
        "muted pastel colors; gentle skin tones", "quiet neutral palette; pale accents", "soft ambient illumination; subtle window light",
        "close quiet framing; intimate negative space", "simple interiors; understated everyday settings", "casual fashion; softly folded fabric",
        "gentle; introspective", "expressions; hands; fabric; small objects",
    ),
    _record(
        "ASK", ("ask", "A-S-K"),
        "stylized digital painting", "fantasy portraiture", "head-and-shoulder studies; solitary characters",
        "crisp selective contours; painterly edge variation", "sculpted angular forms", "defined facial planes; controlled expressions",
        "grounded realistic proportions", "sculpted dimensional rendering; restrained texture", "controlled gradient shading; firm value structure",
        "rich subdued colors; selective accents", "earthy jewel palette; controlled contrast", "focused studio-like lighting; shaped face light",
        "strong portrait framing; deliberate cropping", "minimal tonal backgrounds", "structured fantasy clothing; refined accessories",
        "reserved; commanding", "facial planes; eyes; material edges; accessories",
    ),
    _record(
        "Krenz Cushart", ("Krenz", "KrenzCushart", "Krenz-Cushart"),
        "painterly digital illustration; anatomy-driven concept painting", "dynamic action fantasy", "figures in motion; gesture-centered action scenes",
        "confident structural drawing; energetic broken edge work", "sweeping directional masses; forceful gesture arcs", "solid planar facial construction; animated expressions",
        "convincing anatomical structure; aggressive foreshortening", "broad painterly rendering; clearly modeled material volumes", "strong value construction; decisive cast and bounce shadows",
        "rich varied colors; broad controlled tonal range", "cinematic warm-cool palette; saturated focal accents", "strong directional key light; dramatic colored bounce light",
        "action-oriented diagonal composition; forceful depth movement", "dimensional fantasy spaces; perspective-driven atmospheric distance", "layered action costumes; armor following body mechanics",
        "energetic; instructive", "anatomy; gesture rhythm; light logic; spatial construction",
    ),
    _record(
        "Hiten", ("hiten",),
        "delicate luminous anime illustration; finely finished digital art", "serene romantic fantasy", "quiet character encounters; elegant intimate portraits",
        "clean slender linework; exceptionally fine tapered contours", "long graceful curves; light floating silhouettes", "serene refined faces; translucent jewel-like eyes",
        "slender elegant proportions; gentle posture", "smooth luminous rendering; restrained decorative finish", "soft cel gradients; feathered shadow transitions",
        "pale harmonious coloring; subtle floral accents", "airy pastel palette; cool lavender and sky tones", "gentle backlighting; diffused atmospheric glow",
        "calm lyrical composition; carefully shaped negative space", "quiet scenic backdrops; softly dissolved foliage and sky", "elegant layered clothing; delicate translucent fabric detail",
        "serene; wistful", "eyes; hair strands; fabric edges; ambient glow",
    ),
    _record(
        "Tiv", ("tiv",),
        "contemporary anime illustration", "modern slice-of-life", "everyday character interactions; ensemble scenes",
        "neat consistent linework; crisp readable contours", "clean compact shapes; balanced silhouettes", "clear expressions; neatly constructed faces",
        "natural contemporary proportions", "clean digital rendering; carefully controlled details", "controlled soft shading; readable form separation",
        "clear bright colors; natural skin tones", "fresh balanced palette; modest accents", "fresh natural lighting; clear ambient fill",
        "orderly character-focused composition; readable grouping", "modern interiors; everyday urban spaces", "modern layered clothing; practical fabric details",
        "friendly; observant", "expressions; clothing; gestures; scene objects",
    ),
    _record(
        "Coffee-kizoku", ("Coffee Kizoku", "CoffeeKizoku", "coffee-kizoku"),
        "refined anime portraiture", "elegant contemporary", "calm character portraits; interior scenes",
        "fine polished linework; smooth contours", "graceful vertical forms", "calm faces; glossy carefully shaped eyes",
        "slender composed proportions", "polished smooth rendering; glossy hair treatment", "soft tonal shading; subtle fabric modeling",
        "cool elegant colors; restrained saturation", "navy and neutral palette; pale highlights", "soft window-like illumination; controlled highlights",
        "composed portrait framing; quiet depth", "refined interiors; subdued architectural details", "formal clothing; carefully folded skirts and jackets",
        "quiet; sophisticated", "hair; eyes; fabric folds; window light",
    ),
    _record(
        "BUNBUN", ("bunbun", "Bun Bun"),
        "bold anime illustration", "adventure fantasy", "active characters; heroic groups",
        "firm clean contours; decisive line weight", "clear graphic silhouettes; angular costume shapes", "lively expressions; strongly readable eyes",
        "athletic animated proportions", "crisp graphic rendering; clear material separation", "crisp cel shading; firm shadow shapes",
        "strong primary colors; vivid costume accents", "bright adventurous palette; clear contrasts", "bright directional light; crisp highlights",
        "dynamic readable composition; strong pose flow", "open adventure settings; simplified action backdrops", "adventure costumes; bold armor shapes",
        "lively; heroic", "silhouette; expressions; costume shapes; action gesture",
    ),
    _record(
        "LAM", ("lam", "L-A-M"),
        "high-impact graphic illustration; poster-oriented digital art", "urban pop fantasy", "dramatic close-up portraits; confrontational fashion characters",
        "razor-sharp high-contrast linework; aggressive tapered strokes", "angular geometric forms; fractured silhouette accents", "intense expressions; sharply constructed oversized eyes",
        "stylized elongated proportions; angular poses", "dense graphic rendering; layered print and screen-like surfaces", "hard graphic shadows; stark black value breaks",
        "electric color blocking; bold complementary clashes", "neon magenta-cyan-yellow palette; deep black anchors", "hard frontal graphic lighting; vivid chromatic rim accents",
        "compressed poster composition; extreme dramatic cropping", "abstract urban graphics; layered geometric and typography-like shapes", "street fashion; angular accessories and bold pattern panels",
        "intense; rebellious", "eyes; line contrast; neon blocks; overlapping graphic layers",
    ),
    _record(
        "fuzichoco", ("Fuzichoco", "fuzi choco", "fuzi-choco"),
        "ornate digital illustration", "decorative fantasy", "delicate characters; richly detailed scenes",
        "fine elaborate linework; intricate contour networks", "organic curling forms; densely interlocking motifs", "delicate faces; jewel-like eyes",
        "graceful storybook proportions", "layered decorative rendering; intricate surface ornament", "fine graduated shading; translucent overlaps",
        "jewel-like colors; layered transparent hues", "rich botanical palette; luminous accents", "glowing magical illumination; scattered light points",
        "richly layered composition; dense ornamental depth", "botanical architecture; elaborate fantasy spaces", "ornate fantasy garments; patterned textiles",
        "enchanted; abundant", "flora; ornament; textiles; architectural motifs",
    ),
    _record(
        "SWAV", ("swav", "S-W-A-V"),
        "stylized digital character art", "modern fantasy", "poised character portraits; fashion figures",
        "precise tapered contours; clean selective strokes", "sleek geometric forms; bold centered silhouettes", "sharp facial detail; composed expressions",
        "stylized balanced proportions", "smooth hard-edged rendering; contemporary graphic finish", "controlled planar shading; crisp transitions",
        "controlled saturated colors; clean accent blocks", "limited modern palette; vivid focal accents", "clean contrast lighting; polished highlights",
        "bold centered composition; controlled negative space", "minimal graphic environments", "modern fantasy outfits; sleek material panels",
        "poised; modern", "face; silhouette; material panels; color accents",
    ),
    _record(
        "LM7", ("lm7", "LM-7"),
        "atmospheric digital illustration", "industrial science fiction", "armored characters; environmental scenes",
        "dense technical linework; broken mechanical contours", "compact angular silhouettes; layered machine forms", "restrained facial detail; focused expressions",
        "compact grounded proportions", "textured industrial rendering; layered mechanical surfaces", "low-key tonal shading; deep occlusion shadows",
        "dark restrained colors; selective luminous accents", "charcoal and steel palette; signal-color highlights", "low-key cinematic lighting; localized glow",
        "layered environmental composition; compressed depth", "industrial futuristic settings; atmospheric debris", "armored clothing; modular technical gear",
        "tense; atmospheric", "machinery; armor; surface wear; localized light",
    ),
    _record(
        "Ilya Kuvshinov", ("IlyaKuvshinov", "Ilya-Kuvshinov"),
        "polished digital illustration; anime-influenced portrait painting", "contemporary character portraiture", "fashion-oriented portraits; intimate character close-ups",
        "crisp fine contours; selective painted edges", "clean elongated silhouettes; graphic hair shapes", "large expressive eyes; simplified elegant facial planes",
        "slender contemporary proportions; relaxed poses", "smooth polished portrait rendering; refined skin and hair surfaces", "soft gradient modeling; controlled cel-painterly transitions",
        "restrained modern coloring; subtle tinted skin tones", "cool neutral palette; selective saturated accents", "soft studio illumination; understated cinematic rim light",
        "tight portrait cropping; asymmetric graphic framing", "minimal urban or abstract backdrops", "contemporary fashion; clean layered garments",
        "cool; introspective", "eyes; hair shapes; facial planes; graphic cropping",
    ),
    _record(
        "Mai Yoneyama", ("MaiYoneyama", "Mai-Yoneyama"),
        "mixed-media anime illustration; animation-inspired editorial art", "expressive pop character art", "dynamic characters; gesture-driven fashion figures",
        "loose calligraphic strokes; visible sketch accents", "angular elastic forms; exaggerated gesture shapes", "striking eyes; simplified expressive facial features",
        "stylized flexible anatomy; energetic posing", "layered flat and painted textures; intentionally visible mark-making", "selective graphic shadows; broken tonal patches",
        "bold color overlays; fragmented color transitions", "saturated warm-cool contrasts; unexpected accent hues", "flat graphic illumination; selective luminous glow",
        "asymmetric editorial composition; active negative space", "abstract color fields; floating graphic marks", "experimental fashion silhouettes; layered fabric shapes",
        "energetic; experimental", "gesture; hands; line rhythm; overlapping color shapes",
    ),
    _record(
        "Greg Rutkowski", ("GregRutkowski", "Greg-Rutkowski"),
        "painterly fantasy key art; digital oil-like painting", "epic high fantasy", "heroic figures; creatures within grand landscapes",
        "brush-defined contours; textured broken edges", "monumental triangular masses; sweeping heroic silhouettes", "classically modeled faces; resolute expressions",
        "heroic anatomical proportions; forceful stance", "dense painterly rendering; richly textured brush surfaces", "dramatic value sculpting; deep cast shadows",
        "cinematic warm-cool coloring; glowing atmospheric accents", "warm amber against cool blue-gray; earthy darks", "golden rim lighting; volumetric storm light",
        "central heroic composition; sweeping landscape depth", "ancient ruins; mountains and turbulent skies", "ornate armor; weathered fantasy materials",
        "epic; stormy", "brush texture; dramatic light; armor; environmental scale",
    ),
    _record(
        "Craig Mullins", ("CraigMullins", "Craig-Mullins"),
        "concept painting; digital gouache-like illustration", "cinematic science fantasy", "environment concepts; vehicles and small scale figures",
        "loose brush-defined edges; lost-and-found contours", "large value masses; irregular industrial forms", "minimally stated faces; shape-led figures",
        "small scale figures; natural functional poses", "economical painterly rendering; suggestive material marks", "broad value blocks; selective sharp accents",
        "muted naturalistic coloring; localized chromatic notes", "earth tones and cool grays; sparse warm accents", "motivated cinematic light; broad atmospheric shadow",
        "wide concept-art framing; strong layered depth", "industrial interiors; alien landscapes and distant structures", "utilitarian costumes; minimally described gear",
        "exploratory; atmospheric", "scale cues; value design; architecture; brush economy",
    ),
    _record(
        "Feng Zhu", ("FengZhu", "Feng-Zhu"),
        "industrial design concept art; digital marker-style rendering", "science-fiction production design", "vehicles; architecture and functional equipment",
        "precise construction lines; controlled design contours", "functional geometric forms; engineered modular silhouettes", "minimal facial emphasis; readable scale figures",
        "functional human scale; neutral reference poses", "clear design rendering; explicit material separation", "controlled gradients; informative cast shadows",
        "neutral industrial coloring; practical surface variation", "gray and earth palette; signal-color accents", "clear studio or environmental illumination; readable reflections",
        "perspective-driven design presentation; wide establishing views", "functional interiors; transport and built environments", "utilitarian uniforms; equipment-focused gear",
        "practical; futuristic", "perspective; function; machinery; human scale",
    ),
    _record(
        "Jama Jurabaev", ("JamaJurabaev", "Jama-Jurabaev"),
        "cinematic concept painting; matte-style digital illustration", "narrative science fantasy", "story moments; environments anchored by human figures",
        "selective painted contours; controlled photographic edge integration", "massive silhouettes; brutalist and organic shape contrasts", "restrained realistic faces; narrative expressions",
        "realistic scale figures; grounded movement", "photographic textures integrated with painterly rendering; cohesive surfaces", "cinematic value grouping; deep environmental shadows",
        "desaturated cinematic color grading; localized narrative accents", "earth and cool-gray palette; isolated warm lights", "diffuse haze lighting; dramatic shafts and silhouettes",
        "widescreen film framing; deliberate story blocking", "vast architecture; terrain and atmospheric distance", "weathered practical clothing; narrative equipment",
        "ominous; contemplative", "story beat; scale; atmosphere; directional light",
    ),
    _record(
        "Even Amundsen", ("EvenAmundsen", "Even-Amundsen"),
        "painterly character concept art; textured digital fantasy illustration", "Nordic-inspired fantasy", "rugged characters; design-focused portraits",
        "confident sketch-informed contours; textured edge variation", "broad sturdy silhouettes; carved angular shapes", "characterful faces; weathered expressive features",
        "solid grounded anatomy; weight-bearing poses", "textured painterly rendering; tactile natural materials", "chunky form shading; strong readable planes",
        "earthy restrained coloring; cold atmospheric accents", "desaturated earth palette; iron gray and muted blue", "moody side lighting; cool environmental fill",
        "clear character-design framing; silhouette-first composition", "sparse Nordic landscapes; misty natural backdrops", "layered leather fur and metal; practical fantasy gear",
        "rugged; mythic", "costume construction; silhouette; facial character; material texture",
    ),
    _record(
        "Ruan Jia", ("RuanJia", "Ruan-Jia"),
        "ornate painterly fantasy illustration; high-detail digital painting", "epic eastern-influenced fantasy", "elaborate warriors; magical narrative scenes",
        "fine expressive contours; shifting painterly edges", "flowing interwoven forms; elaborate layered silhouettes", "refined faces; luminous focused eyes",
        "graceful dynamic anatomy; sweeping poses", "high-density painterly rendering; intricate ornamental surfaces", "rich sculpted shading; luminous layered shadows",
        "saturated nuanced coloring; radiant magical effects", "deep jewel-tone palette; controlled warm-cool contrast", "dramatic magical illumination; concentrated glow and rim light",
        "dynamic layered composition; swirling directional movement", "ornate fantasy architecture; luminous atmospheric depth", "elaborate armor and robes; intricate metal and fabric motifs",
        "majestic; mysterious", "ornament; color transitions; armor detail; magical light",
    ),
)


def normalize_artist_name(name):
    """Normalize case and common separator differences for safe lookup."""
    try:
        text = unicodedata.normalize("NFKC", str(name or "")).casefold().strip()
        return "".join(character for character in text if character.isalnum())
    except Exception:
        return ""


_ARTIST_INDEX = {}
for _entry in ARTISTS:
    for _name in (_entry["canonical_name"], *_entry["aliases"]):
        _ARTIST_INDEX[normalize_artist_name(_name)] = _entry


def get_artist(name):
    """Return a defensive copy of a matching record, or None."""
    entry = _ARTIST_INDEX.get(normalize_artist_name(name))
    return deepcopy(entry) if entry is not None else None


def list_artists():
    """Return canonical names sorted without case sensitivity."""
    return sorted((entry["canonical_name"] for entry in ARTISTS), key=str.casefold)
