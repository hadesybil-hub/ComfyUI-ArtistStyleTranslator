"""Built-in structured style profiles for observable visual traits."""

try:
    from .knowledge_base import (
        KnowledgeBaseLoader,
        STYLE_PROFILE_FIELDS,
        legacy_artist_view,
        normalize_artist_name,
        project_semantic_style_profile,
    )
except ImportError:  # Supports the existing direct-file test loader.
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path

    _knowledge_path = Path(__file__).with_name("knowledge_base.py")
    _knowledge_spec = spec_from_file_location(
        "artist_style_translator_standalone_knowledge_base",
        _knowledge_path,
    )
    if _knowledge_spec is None or _knowledge_spec.loader is None:
        raise RuntimeError("Unable to load the artist knowledge base")
    _knowledge_module = module_from_spec(_knowledge_spec)
    _knowledge_spec.loader.exec_module(_knowledge_module)
    KnowledgeBaseLoader = _knowledge_module.KnowledgeBaseLoader
    STYLE_PROFILE_FIELDS = _knowledge_module.STYLE_PROFILE_FIELDS
    legacy_artist_view = _knowledge_module.legacy_artist_view
    normalize_artist_name = _knowledge_module.normalize_artist_name
    project_semantic_style_profile = (
        _knowledge_module.project_semantic_style_profile
    )


def _phrases(value):
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(part.strip() for part in value.split(";") if part.strip())
    return tuple(str(part).strip() for part in value if str(part).strip())


def _record(*, artist_id, canonical_name, aliases, **profile_values):
    if set(profile_values) != set(STYLE_PROFILE_FIELDS):
        missing = sorted(set(STYLE_PROFILE_FIELDS) - set(profile_values))
        unknown = sorted(set(profile_values) - set(STYLE_PROFILE_FIELDS))
        raise ValueError(
            f"Style profile fields are invalid; missing={missing}, unknown={unknown}"
        )
    style_profile = {
        field: _phrases(profile_values[field])
        for field in STYLE_PROFILE_FIELDS
    }
    return {
        "artist_id": artist_id,
        "canonical_name": canonical_name,
        "display_name": canonical_name,
        "aliases": tuple(aliases),
        "localized_names": {},
        "category": ("legacy_builtin",),
        "metadata": {
            "source": "legacy_migration",
            "version": "1.0.0",
            "created_at": "2026-07-22T13:52:45+08:00",
            "updated_at": "2026-07-22T13:52:45+08:00",
            "profile_schema_version": "1.0",
            "review_status": "published",
        },
        "semantic": {
            "style_profile": style_profile,
            "profile_confidence": 0.95,
            "category_confidence": {
                field: 0.95 for field in STYLE_PROFILE_FIELDS
            },
            "evidence": (
                {
                    "evidence_id": f"legacy:{artist_id}:profile",
                    "type": "legacy_migration",
                    "scope": "profile",
                    "summary": (
                        "Migrated from the pre-V1.7 built-in structured style "
                        "profile without claiming new research provenance."
                    ),
                    "reference": "artist_database.py@1562858",
                },
            ),
        },
    }


def _curated_record(
    *,
    artist_id,
    canonical_name,
    display_name,
    aliases,
    localized_names,
    category,
    metadata,
    profile_confidence,
    category_confidence,
    evidence,
    **profile_values,
):
    """Build a researched record while keeping all 17 dimensions named."""
    if set(profile_values) != set(STYLE_PROFILE_FIELDS):
        missing = sorted(set(STYLE_PROFILE_FIELDS) - set(profile_values))
        unknown = sorted(set(profile_values) - set(STYLE_PROFILE_FIELDS))
        raise ValueError(
            f"Style profile fields are invalid; missing={missing}, unknown={unknown}"
        )
    return {
        "artist_id": artist_id,
        "canonical_name": canonical_name,
        "display_name": display_name,
        "aliases": tuple(aliases),
        "localized_names": {
            language: tuple(names)
            for language, names in localized_names.items()
        },
        "category": tuple(category),
        "metadata": dict(metadata),
        "semantic": {
            "style_profile": {
                field: _phrases(profile_values[field])
                for field in STYLE_PROFILE_FIELDS
            },
            "profile_confidence": profile_confidence,
            "category_confidence": dict(category_confidence),
            "evidence": tuple(evidence),
        },
    }


KNOWLEDGE_RECORDS = (
    _record(
        artist_id='yaegashi-nan', canonical_name="Yaegashi Nan", aliases=("YaegashiNan", "Yaegashi-Nan"),
        medium="anime character illustration", genre="mature character portraiture", subject_focus="expressive character portraits; full-body figures",
        linework="clean delicate linework; tapered contours", shape_language="elegant flowing shapes", facial_design="refined facial features; expressive almond-shaped eyes",
        anatomy="graceful elongated proportions", rendering="smooth polished rendering; carefully finished surfaces", shading="soft cel shading; controlled tonal transitions",
        coloring="smooth skin tones; nuanced fabric colors", palette="warm controlled palette; restrained accents", lighting="warm soft illumination; subtle rim light",
        composition="balanced character-centered framing; clear focal hierarchy", environment="minimal atmospheric backdrop", clothing="detailed clothing folds; elegant fitted garments",
        mood="composed; gently expressive", detail_emphasis="faces; eyes; fabric folds; hair strands",
    ),
    _record(
        artist_id='tony-taka', canonical_name="Tony Taka", aliases=("Tony", "TonyTaka", "Tony-Taka"),
        medium="polished anime illustration", genre="romantic fantasy", subject_focus="graceful character portraits; paired figures",
        linework="fine continuous contours; soft edge control", shape_language="flowing rounded silhouettes", facial_design="softly modeled faces; luminous rounded eyes",
        anatomy="slender balanced proportions", rendering="glossy refined rendering; smooth surface finish", shading="gentle gradient shading; soft form modeling",
        coloring="rich harmonious colors; luminous skin tones", palette="jewel tones balanced with pastels", lighting="soft radiant lighting; delicate highlights",
        composition="calm symmetrical framing; layered portrait depth", environment="ornamental fantasy settings", clothing="flowing fantasy costumes; decorative accessories",
        mood="romantic; serene", detail_emphasis="eyes; hair; fabric; ornamental details",
    ),
    _record(
        artist_id='kantoku', canonical_name="Kantoku", aliases=("Kantoku-Artist",),
        medium="clean anime illustration", genre="slice-of-life", subject_focus="youthful characters; everyday interactions",
        linework="precise lightweight linework; crisp contours", shape_language="light compact silhouettes", facial_design="delicate faces; bright readable eyes",
        anatomy="youthful natural proportions", rendering="clean digital rendering; tidy surface detail", shading="light cel shading; gentle gradients",
        coloring="fresh pastel-leaning colors", palette="bright airy palette; soft accent colors", lighting="clear daylight; diffuse ambient glow",
        composition="spacious balanced layouts; casual scene framing", environment="bright interiors; open everyday spaces", clothing="casual layered clothing; small fashion details",
        mood="cheerful; relaxed", detail_emphasis="facial expressions; clothing details; everyday objects",
    ),
    _record(
        artist_id='mika-pikazo', canonical_name="Mika Pikazo", aliases=("MikaPikazo", "Mika-Pikazo"),
        medium="graphic digital illustration", genre="pop fantasy", subject_focus="energetic character portraits; fashion-focused figures",
        linework="sharp confident contours; varied graphic strokes", shape_language="angular layered shapes; bold silhouette breaks", facial_design="stylized facial geometry; intense expressive eyes",
        anatomy="dynamic fashion proportions", rendering="high-impact graphic rendering; layered decorative surfaces", shading="hard-edged cel shading; abrupt color transitions",
        coloring="high-saturation color blocking; vivid accents", palette="electric complementary palette; multicolor contrasts", lighting="bright punchy illumination; graphic highlights",
        composition="dynamic poster framing; dense asymmetric balance", environment="abstract decorative backdrops; layered symbols", clothing="fashion-forward costumes; graphic accessories",
        mood="energetic; playful", detail_emphasis="eyes; color blocks; accessories; decorative shapes",
    ),
    _record(
        artist_id='lack', canonical_name="lack", aliases=("Lack", "lackartist"),
        medium="polished digital character illustration; crisp fantasy portrait art", genre="ornamental dark fantasy", subject_focus="commanding character portraits; design-focused fantasy figures",
        linework="controlled angular linework; crisp selective edge accents", shape_language="strong tapered silhouettes; intricate ornamental geometry", facial_design="defined facial planes; focused jewel-like eyes",
        anatomy="athletic heroic proportions; poised stance", rendering="high-clarity dimensional rendering; meticulously separated materials", shading="firm planar shading; deep sculpted shadows",
        coloring="deep chromatic fields; selective vivid accents", palette="dark jewel palette; concentrated warm highlights", lighting="focused theatrical lighting; narrow luminous rim light",
        composition="iconic centered portrait composition; layered character depth", environment="abstract dark fantasy atmosphere; restrained background motifs", clothing="ornate layered fantasy costumes; finely designed metal accessories",
        mood="intense; ceremonial", detail_emphasis="facial focus; ornament; armor materials; silhouette edges",
    ),
    _record(
        artist_id='redjuice', canonical_name="redjuice", aliases=("Redjuice", "red-juice"),
        medium="cinematic science-fiction illustration; sleek digital concept art", genre="near-future visual narrative", subject_focus="futuristic characters; technology-centered urban scenes",
        linework="fine technical linework; precise luminous edge accents", shape_language="elongated aerodynamic forms; interlocking mechanical geometry", facial_design="refined angular faces; narrow sharply lit eyes",
        anatomy="slender stylized proportions; controlled gesture", rendering="layered atmospheric rendering; intricate synthetic surface treatment", shading="smooth tonal modeling; deep transparent ambient shadows",
        coloring="cool cinematic color grading; restrained signal-color accents", palette="blue-gray and cyan palette; isolated luminous highlights", lighting="moody directional lighting; electric rim glow",
        composition="asymmetric cinematic framing; strong foreground-to-background depth", environment="dense futuristic city structures; illuminated atmospheric haze", clothing="technical garments; segmented armor and translucent panels",
        mood="tense; futuristic", detail_emphasis="interface-like details; synthetic materials; haze; luminous edges",
    ),
    _record(
        artist_id='wlop', canonical_name="WLOP", aliases=("wlop", "W-LOP"),
        medium="atmospheric digital painting; painterly fantasy illustration", genre="cinematic environmental fantasy", subject_focus="environmental storytelling; figures within expansive fantasy worlds",
        linework="soft painterly edge transitions; minimally visible contours", shape_language="elegant flowing silhouettes; monumental sweeping forms", facial_design="realistic facial modeling; restrained expressions",
        anatomy="graceful proportions within large scenes", rendering="layered atmospheric rendering; character integrated with environment", shading="blended tonal transitions; forms softened by atmosphere",
        coloring="muted cinematic color grading; atmospheric depth colors", palette="subdued cool-warm palette; restrained jewel accents", lighting="volumetric haze lighting; distant luminous atmosphere",
        composition="wide cinematic composition; character embedded in a large-scale world", environment="large-scale world building; mist-filled architecture", clothing="flowing garments shaped by wind; painterly fabric",
        mood="dramatic; contemplative", detail_emphasis="environmental scale; atmosphere; silhouette; narrative space",
    ),
    _record(
        artist_id='guweiz', canonical_name="Guweiz", aliases=("guweiz", "Gu Wei Zi"),
        medium="polished digital character illustration; game character concept art", genre="heroic fantasy concept art", subject_focus="single heroic characters; costume-centered presentation",
        linework="clean controlled contours; precise costume detailing", shape_language="strong heroic silhouette; armor-driven shape design", facial_design="realistic anime-influenced facial design; focused expressions",
        anatomy="grounded heroic anatomy; confident stance", rendering="polished fantasy character rendering; detailed material finish", shading="firm dimensional shading; defined armor planes",
        coloring="rich controlled character colors; distinct material separation", palette="deep fantasy palette; focused accent colors", lighting="dramatic character lighting; strong directional highlights",
        composition="heroic character presentation; full-figure concept framing", environment="restrained atmospheric backdrop; secondary environmental detail", clothing="detailed armor and clothing design; layered game costume elements",
        mood="resolute; adventurous", detail_emphasis="costume construction; armor; silhouette; character materials",
    ),
    _record(
        artist_id='sakimichan', canonical_name="Sakimichan", aliases=("saki michan", "Saki-michan"),
        medium="semi-realistic digital painting; CG character illustration", genre="game promotional character art", subject_focus="glamorous character portraits; anatomy-focused figures",
        linework="soft polished contours; clean facial edges", shape_language="sculpted body forms; curved glamorous silhouettes", facial_design="refined facial beauty; glossy expressive eyes",
        anatomy="detailed anatomy rendering; idealized proportions", rendering="highly polished character rendering; smooth skin finish", shading="smooth volumetric modeling; carefully blended form shading",
        coloring="luminous skin coloring; glossy material treatment", palette="rich saturated palette; warm skin-focused harmony", lighting="strong rim lighting; glossy specular highlights",
        composition="character-dominant promotional framing; dramatic close composition", environment="minimal fantasy or studio backdrop", clothing="form-fitting detailed costumes; reflective fabric and armor",
        mood="glamorous; dramatic", detail_emphasis="facial beauty; skin; anatomy; glossy materials",
    ),
    _record(
        artist_id='artgerm', canonical_name="Artgerm", aliases=("art germ", "Stanley Artgerm Lau"),
        medium="commercial digital illustration; comic-influenced character art", genre="hero portraiture", subject_focus="sharp character focus; iconic individual heroes",
        linework="clean confident linework; sharp controlled edges", shape_language="bold elegant silhouette; balanced graphic shapes", facial_design="elegant facial features; clear heroic expression",
        anatomy="idealized comic-informed anatomy; poised proportions", rendering="clean polished rendering; premium illustration finish", shading="controlled smooth shading; crisp form definition",
        coloring="controlled commercial colors; clean local color separation", palette="balanced graphic palette; selective vivid accents", lighting="clean studio lighting; precise focal highlights",
        composition="hero portrait composition; balanced graphic composition", environment="minimal supporting backdrop; graphic negative space", clothing="refined hero costumes; clearly designed accessories",
        mood="confident; aspirational", detail_emphasis="face; silhouette; graphic balance; premium finish",
    ),
    _record(
        artist_id='rella', canonical_name="Rella", aliases=("rella",),
        medium="luminous digital illustration", genre="dreamlike fantasy", subject_focus="ethereal character portraits; floating figures",
        linework="fine luminous linework; delicate broken contours", shape_language="light floating forms; translucent layers", facial_design="delicate faces; sparkling reflective eyes",
        anatomy="slender weightless proportions", rendering="translucent layered rendering; sparkling surface effects", shading="soft diffused shading; glowing tonal transitions",
        coloring="pastel gradients; iridescent accents", palette="pearl-like palette; cool luminous pastels", lighting="glowing diffused light; scattered highlights",
        composition="airy layered composition; generous negative space", environment="dreamlike atmospheric spaces; floating particles", clothing="light translucent garments; delicate ornaments",
        mood="ethereal; hopeful", detail_emphasis="light effects; eyes; translucent fabric; particles",
    ),
    _record(
        artist_id='nardack', canonical_name="Nardack", aliases=("nardack",),
        medium="polished anime illustration", genre="decorative fantasy", subject_focus="elegant character portraits; poised figures",
        linework="smooth precise contours; fine decorative lines", shape_language="slender curved silhouettes", facial_design="gentle faces; glossy expressive eyes",
        anatomy="elongated graceful proportions", rendering="smooth glossy rendering; ornamental surface finish", shading="soft cel gradients; subtle form shading",
        coloring="harmonious soft colors; polished highlights", palette="pastel jewel palette; balanced accents", lighting="gentle luminous lighting; soft rim glow",
        composition="balanced portrait framing; graceful visual flow", environment="decorative fantasy backdrops", clothing="ornate costumes; delicate accessories",
        mood="elegant; calm", detail_emphasis="eyes; hair; ornaments; costume trim",
    ),
    _record(
        artist_id='anmi', canonical_name="Anmi", aliases=("anmi",),
        medium="soft anime illustration", genre="intimate slice-of-life", subject_focus="quiet character portraits; gentle everyday moments",
        linework="thin understated linework; soft contours", shape_language="light graceful forms; compact silhouettes", facial_design="subtle expressions; softly defined eyes",
        anatomy="natural youthful proportions", rendering="delicate low-contrast rendering; restrained detail", shading="soft ambient shading; shallow tonal range",
        coloring="muted pastel colors; gentle skin tones", palette="quiet neutral palette; pale accents", lighting="soft ambient illumination; subtle window light",
        composition="close quiet framing; intimate negative space", environment="simple interiors; understated everyday settings", clothing="casual fashion; softly folded fabric",
        mood="gentle; introspective", detail_emphasis="expressions; hands; fabric; small objects",
    ),
    _record(
        artist_id='ask', canonical_name="ASK", aliases=("ask", "A-S-K"),
        medium="stylized digital painting", genre="fantasy portraiture", subject_focus="head-and-shoulder studies; solitary characters",
        linework="crisp selective contours; painterly edge variation", shape_language="sculpted angular forms", facial_design="defined facial planes; controlled expressions",
        anatomy="grounded realistic proportions", rendering="sculpted dimensional rendering; restrained texture", shading="controlled gradient shading; firm value structure",
        coloring="rich subdued colors; selective accents", palette="earthy jewel palette; controlled contrast", lighting="focused studio-like lighting; shaped face light",
        composition="strong portrait framing; deliberate cropping", environment="minimal tonal backgrounds", clothing="structured fantasy clothing; refined accessories",
        mood="reserved; commanding", detail_emphasis="facial planes; eyes; material edges; accessories",
    ),
    _record(
        artist_id='krenz-cushart', canonical_name="Krenz Cushart", aliases=("Krenz", "KrenzCushart", "Krenz-Cushart"),
        medium="painterly digital illustration; anatomy-driven concept painting", genre="dynamic action fantasy", subject_focus="figures in motion; gesture-centered action scenes",
        linework="confident structural drawing; energetic broken edge work", shape_language="sweeping directional masses; forceful gesture arcs", facial_design="solid planar facial construction; animated expressions",
        anatomy="convincing anatomical structure; aggressive foreshortening", rendering="broad painterly rendering; clearly modeled material volumes", shading="strong value construction; decisive cast and bounce shadows",
        coloring="rich varied colors; broad controlled tonal range", palette="cinematic warm-cool palette; saturated focal accents", lighting="strong directional key light; dramatic colored bounce light",
        composition="action-oriented diagonal composition; forceful depth movement", environment="dimensional fantasy spaces; perspective-driven atmospheric distance", clothing="layered action costumes; armor following body mechanics",
        mood="energetic; instructive", detail_emphasis="anatomy; gesture rhythm; light logic; spatial construction",
    ),
    _record(
        artist_id='hiten', canonical_name="Hiten", aliases=("hiten",),
        medium="delicate luminous anime illustration; finely finished digital art", genre="serene romantic fantasy", subject_focus="quiet character encounters; elegant intimate portraits",
        linework="clean slender linework; exceptionally fine tapered contours", shape_language="long graceful curves; light floating silhouettes", facial_design="serene refined faces; translucent jewel-like eyes",
        anatomy="slender elegant proportions; gentle posture", rendering="smooth luminous rendering; restrained decorative finish", shading="soft cel gradients; feathered shadow transitions",
        coloring="pale harmonious coloring; subtle floral accents", palette="airy pastel palette; cool lavender and sky tones", lighting="gentle backlighting; diffused atmospheric glow",
        composition="calm lyrical composition; carefully shaped negative space", environment="quiet scenic backdrops; softly dissolved foliage and sky", clothing="elegant layered clothing; delicate translucent fabric detail",
        mood="serene; wistful", detail_emphasis="eyes; hair strands; fabric edges; ambient glow",
    ),
    _record(
        artist_id='tiv', canonical_name="Tiv", aliases=("tiv",),
        medium="contemporary anime illustration", genre="modern slice-of-life", subject_focus="everyday character interactions; ensemble scenes",
        linework="neat consistent linework; crisp readable contours", shape_language="clean compact shapes; balanced silhouettes", facial_design="clear expressions; neatly constructed faces",
        anatomy="natural contemporary proportions", rendering="clean digital rendering; carefully controlled details", shading="controlled soft shading; readable form separation",
        coloring="clear bright colors; natural skin tones", palette="fresh balanced palette; modest accents", lighting="fresh natural lighting; clear ambient fill",
        composition="orderly character-focused composition; readable grouping", environment="modern interiors; everyday urban spaces", clothing="modern layered clothing; practical fabric details",
        mood="friendly; observant", detail_emphasis="expressions; clothing; gestures; scene objects",
    ),
    _record(
        artist_id='coffee-kizoku', canonical_name="Coffee-kizoku", aliases=("Coffee Kizoku", "CoffeeKizoku", "coffee-kizoku"),
        medium="refined anime portraiture", genre="elegant contemporary", subject_focus="calm character portraits; interior scenes",
        linework="fine polished linework; smooth contours", shape_language="graceful vertical forms", facial_design="calm faces; glossy carefully shaped eyes",
        anatomy="slender composed proportions", rendering="polished smooth rendering; glossy hair treatment", shading="soft tonal shading; subtle fabric modeling",
        coloring="cool elegant colors; restrained saturation", palette="navy and neutral palette; pale highlights", lighting="soft window-like illumination; controlled highlights",
        composition="composed portrait framing; quiet depth", environment="refined interiors; subdued architectural details", clothing="formal clothing; carefully folded skirts and jackets",
        mood="quiet; sophisticated", detail_emphasis="hair; eyes; fabric folds; window light",
    ),
    _record(
        artist_id='bunbun', canonical_name="BUNBUN", aliases=("bunbun", "Bun Bun"),
        medium="bold anime illustration", genre="adventure fantasy", subject_focus="active characters; heroic groups",
        linework="firm clean contours; decisive line weight", shape_language="clear graphic silhouettes; angular costume shapes", facial_design="lively expressions; strongly readable eyes",
        anatomy="athletic animated proportions", rendering="crisp graphic rendering; clear material separation", shading="crisp cel shading; firm shadow shapes",
        coloring="strong primary colors; vivid costume accents", palette="bright adventurous palette; clear contrasts", lighting="bright directional light; crisp highlights",
        composition="dynamic readable composition; strong pose flow", environment="open adventure settings; simplified action backdrops", clothing="adventure costumes; bold armor shapes",
        mood="lively; heroic", detail_emphasis="silhouette; expressions; costume shapes; action gesture",
    ),
    _record(
        artist_id='lam', canonical_name="LAM", aliases=("lam", "L-A-M"),
        medium="high-impact graphic illustration; poster-oriented digital art", genre="urban pop fantasy", subject_focus="dramatic close-up portraits; confrontational fashion characters",
        linework="razor-sharp high-contrast linework; aggressive tapered strokes", shape_language="angular geometric forms; fractured silhouette accents", facial_design="intense expressions; sharply constructed oversized eyes",
        anatomy="stylized elongated proportions; angular poses", rendering="dense graphic rendering; layered print and screen-like surfaces", shading="hard graphic shadows; stark black value breaks",
        coloring="electric color blocking; bold complementary clashes", palette="neon magenta-cyan-yellow palette; deep black anchors", lighting="hard frontal graphic lighting; vivid chromatic rim accents",
        composition="compressed poster composition; extreme dramatic cropping", environment="abstract urban graphics; layered geometric and typography-like shapes", clothing="street fashion; angular accessories and bold pattern panels",
        mood="intense; rebellious", detail_emphasis="eyes; line contrast; neon blocks; overlapping graphic layers",
    ),
    _record(
        artist_id='fuzichoco', canonical_name="fuzichoco", aliases=("Fuzichoco", "fuzi choco", "fuzi-choco"),
        medium="ornate digital illustration", genre="decorative fantasy", subject_focus="delicate characters; richly detailed scenes",
        linework="fine elaborate linework; intricate contour networks", shape_language="organic curling forms; densely interlocking motifs", facial_design="delicate faces; jewel-like eyes",
        anatomy="graceful storybook proportions", rendering="layered decorative rendering; intricate surface ornament", shading="fine graduated shading; translucent overlaps",
        coloring="jewel-like colors; layered transparent hues", palette="rich botanical palette; luminous accents", lighting="glowing magical illumination; scattered light points",
        composition="richly layered composition; dense ornamental depth", environment="botanical architecture; elaborate fantasy spaces", clothing="ornate fantasy garments; patterned textiles",
        mood="enchanted; abundant", detail_emphasis="flora; ornament; textiles; architectural motifs",
    ),
    _record(
        artist_id='swav', canonical_name="SWAV", aliases=("swav", "S-W-A-V"),
        medium="stylized digital character art", genre="modern fantasy", subject_focus="poised character portraits; fashion figures",
        linework="precise tapered contours; clean selective strokes", shape_language="sleek geometric forms; bold centered silhouettes", facial_design="sharp facial detail; composed expressions",
        anatomy="stylized balanced proportions", rendering="smooth hard-edged rendering; contemporary graphic finish", shading="controlled planar shading; crisp transitions",
        coloring="controlled saturated colors; clean accent blocks", palette="limited modern palette; vivid focal accents", lighting="clean contrast lighting; polished highlights",
        composition="bold centered composition; controlled negative space", environment="minimal graphic environments", clothing="modern fantasy outfits; sleek material panels",
        mood="poised; modern", detail_emphasis="face; silhouette; material panels; color accents",
    ),
    _record(
        artist_id='lm7', canonical_name="LM7", aliases=("lm7", "LM-7"),
        medium="atmospheric digital illustration", genre="industrial science fiction", subject_focus="armored characters; environmental scenes",
        linework="dense technical linework; broken mechanical contours", shape_language="compact angular silhouettes; layered machine forms", facial_design="restrained facial detail; focused expressions",
        anatomy="compact grounded proportions", rendering="textured industrial rendering; layered mechanical surfaces", shading="low-key tonal shading; deep occlusion shadows",
        coloring="dark restrained colors; selective luminous accents", palette="charcoal and steel palette; signal-color highlights", lighting="low-key cinematic lighting; localized glow",
        composition="layered environmental composition; compressed depth", environment="industrial futuristic settings; atmospheric debris", clothing="armored clothing; modular technical gear",
        mood="tense; atmospheric", detail_emphasis="machinery; armor; surface wear; localized light",
    ),
    _record(
        artist_id='ilya-kuvshinov', canonical_name="Ilya Kuvshinov", aliases=("IlyaKuvshinov", "Ilya-Kuvshinov"),
        medium="polished digital illustration; anime-influenced portrait painting", genre="contemporary character portraiture", subject_focus="fashion-oriented portraits; intimate character close-ups",
        linework="crisp fine contours; selective painted edges", shape_language="clean elongated silhouettes; graphic hair shapes", facial_design="large expressive eyes; simplified elegant facial planes",
        anatomy="slender contemporary proportions; relaxed poses", rendering="smooth polished portrait rendering; refined skin and hair surfaces", shading="soft gradient modeling; controlled cel-painterly transitions",
        coloring="restrained modern coloring; subtle tinted skin tones", palette="cool neutral palette; selective saturated accents", lighting="soft studio illumination; understated cinematic rim light",
        composition="tight portrait cropping; asymmetric graphic framing", environment="minimal urban or abstract backdrops", clothing="contemporary fashion; clean layered garments",
        mood="cool; introspective", detail_emphasis="eyes; hair shapes; facial planes; graphic cropping",
    ),
    _record(
        artist_id='mai-yoneyama', canonical_name="Mai Yoneyama", aliases=("MaiYoneyama", "Mai-Yoneyama"),
        medium="mixed-media anime illustration; animation-inspired editorial art", genre="expressive pop character art", subject_focus="dynamic characters; gesture-driven fashion figures",
        linework="loose calligraphic strokes; visible sketch accents", shape_language="angular elastic forms; exaggerated gesture shapes", facial_design="striking eyes; simplified expressive facial features",
        anatomy="stylized flexible anatomy; energetic posing", rendering="layered flat and painted textures; intentionally visible mark-making", shading="selective graphic shadows; broken tonal patches",
        coloring="bold color overlays; fragmented color transitions", palette="saturated warm-cool contrasts; unexpected accent hues", lighting="flat graphic illumination; selective luminous glow",
        composition="asymmetric editorial composition; active negative space", environment="abstract color fields; floating graphic marks", clothing="experimental fashion silhouettes; layered fabric shapes",
        mood="energetic; experimental", detail_emphasis="gesture; hands; line rhythm; overlapping color shapes",
    ),
    _record(
        artist_id='greg-rutkowski', canonical_name="Greg Rutkowski", aliases=("GregRutkowski", "Greg-Rutkowski"),
        medium="painterly fantasy key art; digital oil-like painting", genre="epic high fantasy", subject_focus="heroic figures; creatures within grand landscapes",
        linework="brush-defined contours; textured broken edges", shape_language="monumental triangular masses; sweeping heroic silhouettes", facial_design="classically modeled faces; resolute expressions",
        anatomy="heroic anatomical proportions; forceful stance", rendering="dense painterly rendering; richly textured brush surfaces", shading="dramatic value sculpting; deep cast shadows",
        coloring="cinematic warm-cool coloring; glowing atmospheric accents", palette="warm amber against cool blue-gray; earthy darks", lighting="golden rim lighting; volumetric storm light",
        composition="central heroic composition; sweeping landscape depth", environment="ancient ruins; mountains and turbulent skies", clothing="ornate armor; weathered fantasy materials",
        mood="epic; stormy", detail_emphasis="brush texture; dramatic light; armor; environmental scale",
    ),
    _record(
        artist_id='craig-mullins', canonical_name="Craig Mullins", aliases=("CraigMullins", "Craig-Mullins"),
        medium="concept painting; digital gouache-like illustration", genre="cinematic science fantasy", subject_focus="environment concepts; vehicles and small scale figures",
        linework="loose brush-defined edges; lost-and-found contours", shape_language="large value masses; irregular industrial forms", facial_design="minimally stated faces; shape-led figures",
        anatomy="small scale figures; natural functional poses", rendering="economical painterly rendering; suggestive material marks", shading="broad value blocks; selective sharp accents",
        coloring="muted naturalistic coloring; localized chromatic notes", palette="earth tones and cool grays; sparse warm accents", lighting="motivated cinematic light; broad atmospheric shadow",
        composition="wide concept-art framing; strong layered depth", environment="industrial interiors; alien landscapes and distant structures", clothing="utilitarian costumes; minimally described gear",
        mood="exploratory; atmospheric", detail_emphasis="scale cues; value design; architecture; brush economy",
    ),
    _record(
        artist_id='feng-zhu', canonical_name="Feng Zhu", aliases=("FengZhu", "Feng-Zhu"),
        medium="industrial design concept art; digital marker-style rendering", genre="science-fiction production design", subject_focus="vehicles; architecture and functional equipment",
        linework="precise construction lines; controlled design contours", shape_language="functional geometric forms; engineered modular silhouettes", facial_design="minimal facial emphasis; readable scale figures",
        anatomy="functional human scale; neutral reference poses", rendering="clear design rendering; explicit material separation", shading="controlled gradients; informative cast shadows",
        coloring="neutral industrial coloring; practical surface variation", palette="gray and earth palette; signal-color accents", lighting="clear studio or environmental illumination; readable reflections",
        composition="perspective-driven design presentation; wide establishing views", environment="functional interiors; transport and built environments", clothing="utilitarian uniforms; equipment-focused gear",
        mood="practical; futuristic", detail_emphasis="perspective; function; machinery; human scale",
    ),
    _record(
        artist_id='jama-jurabaev', canonical_name="Jama Jurabaev", aliases=("JamaJurabaev", "Jama-Jurabaev"),
        medium="cinematic concept painting; matte-style digital illustration", genre="narrative science fantasy", subject_focus="story moments; environments anchored by human figures",
        linework="selective painted contours; controlled photographic edge integration", shape_language="massive silhouettes; brutalist and organic shape contrasts", facial_design="restrained realistic faces; narrative expressions",
        anatomy="realistic scale figures; grounded movement", rendering="photographic textures integrated with painterly rendering; cohesive surfaces", shading="cinematic value grouping; deep environmental shadows",
        coloring="desaturated cinematic color grading; localized narrative accents", palette="earth and cool-gray palette; isolated warm lights", lighting="diffuse haze lighting; dramatic shafts and silhouettes",
        composition="widescreen film framing; deliberate story blocking", environment="vast architecture; terrain and atmospheric distance", clothing="weathered practical clothing; narrative equipment",
        mood="ominous; contemplative", detail_emphasis="story beat; scale; atmosphere; directional light",
    ),
    _record(
        artist_id='even-amundsen', canonical_name="Even Amundsen", aliases=("EvenAmundsen", "Even-Amundsen"),
        medium="painterly character concept art; textured digital fantasy illustration", genre="Nordic-inspired fantasy", subject_focus="rugged characters; design-focused portraits",
        linework="confident sketch-informed contours; textured edge variation", shape_language="broad sturdy silhouettes; carved angular shapes", facial_design="characterful faces; weathered expressive features",
        anatomy="solid grounded anatomy; weight-bearing poses", rendering="textured painterly rendering; tactile natural materials", shading="chunky form shading; strong readable planes",
        coloring="earthy restrained coloring; cold atmospheric accents", palette="desaturated earth palette; iron gray and muted blue", lighting="moody side lighting; cool environmental fill",
        composition="clear character-design framing; silhouette-first composition", environment="sparse Nordic landscapes; misty natural backdrops", clothing="layered leather fur and metal; practical fantasy gear",
        mood="rugged; mythic", detail_emphasis="costume construction; silhouette; facial character; material texture",
    ),
    _record(
        artist_id='ruan-jia', canonical_name="Ruan Jia", aliases=("RuanJia", "Ruan-Jia"),
        medium="ornate painterly fantasy illustration; high-detail digital painting", genre="epic eastern-influenced fantasy", subject_focus="elaborate warriors; magical narrative scenes",
        linework="fine expressive contours; shifting painterly edges", shape_language="flowing interwoven forms; elaborate layered silhouettes", facial_design="refined faces; luminous focused eyes",
        anatomy="graceful dynamic anatomy; sweeping poses", rendering="high-density painterly rendering; intricate ornamental surfaces", shading="rich sculpted shading; luminous layered shadows",
        coloring="saturated nuanced coloring; radiant magical effects", palette="deep jewel-tone palette; controlled warm-cool contrast", lighting="dramatic magical illumination; concentrated glow and rim light",
        composition="dynamic layered composition; swirling directional movement", environment="ornate fantasy architecture; luminous atmospheric depth", clothing="elaborate armor and robes; intricate metal and fabric motifs",
        mood="majestic; mysterious", detail_emphasis="ornament; color transitions; armor detail; magical light",
    ),
    _curated_record(
        artist_id="homare",
        canonical_name="Homare",
        display_name="Homare",
        aliases=("homare_works",),
        localized_names={"ja": ("誉",)},
        category=("illustrator", "character_designer"),
        metadata={
            "source": "curated_primary_source_review",
            "version": "1.0.0",
            "created_at": "2026-07-22T00:00:00+08:00",
            "updated_at": "2026-07-22T00:00:00+08:00",
            "profile_schema_version": "1.0",
            "review_status": "published",
        },
        profile_confidence=0.85,
        category_confidence={
            "medium": 0.90,
            "genre": 0.85,
            "subject_focus": 0.90,
            "linework": 0.85,
            "shape_language": 0.85,
            "facial_design": 0.85,
            "anatomy": 0.85,
            "rendering": 0.90,
            "shading": 0.85,
            "coloring": 0.85,
            "palette": 0.80,
            "lighting": 0.85,
            "composition": 0.90,
            "environment": 0.80,
            "clothing": 0.90,
            "mood": 0.80,
            "detail_emphasis": 0.90,
        },
        evidence=(
            {
                "evidence_id": "homare:2019-2020:fantasy-character-cards",
                "type": "direct_observation",
                "scope": "profile",
                "summary": (
                    "Seiros, Azura, and Eremiya show character-led vertical "
                    "framing, refined anime-influenced faces, controlled "
                    "contours, layered garments, and carefully separated "
                    "fabric and metal surfaces."
                ),
                "reference": (
                    "https://homareworks.blog.fc2.com/blog-entry-40.html; "
                    "https://homareworks.blog.fc2.com/blog-entry-42.html; "
                    "https://homareworks.blog.fc2.com/blog-entry-45.html"
                ),
            },
            {
                "evidence_id": "homare:2020-2023:publishing-and-game-art",
                "type": "cross_work_synthesis",
                "scope": "profile",
                "summary": (
                    "Slave Reincarnation, Ryuho, Shinohara Yasunoshin, "
                    "Wu Jiang, and the Touhou LostWord card support polished "
                    "painterly modeling, readable silhouettes, grounded "
                    "poses, nuanced materials, and restrained atmospheric "
                    "settings across publishing and game contexts."
                ),
                "reference": (
                    "https://homareworks.blog.fc2.com/blog-entry-46.html; "
                    "https://homareworks.blog.fc2.com/blog-entry-61.html; "
                    "https://homareworks.blog.fc2.com/blog-entry-65.html; "
                    "https://homareworks.blog.fc2.com/blog-entry-73.html; "
                    "https://homareworks.blog.fc2.com/blog-entry-74.html"
                ),
            },
            {
                "evidence_id": "homare:2023-2025:cover-and-mecha-art",
                "type": "cross_work_synthesis",
                "scope": "profile",
                "summary": (
                    "Black Canary, Optimus Prime, and Banagher with Unicorn "
                    "Gundam extend the same figure-first hierarchy and "
                    "material precision into comic covers and mechanical "
                    "subjects, with diagonal action and selective rim glow."
                ),
                "reference": (
                    "https://homareworks.blog.fc2.com/blog-entry-75.html; "
                    "https://homareworks.blog.fc2.com/blog-entry-80.html; "
                    "https://homareworks.blog.fc2.com/blog-entry-81.html"
                ),
            },
            {
                "evidence_id": "homare:2024:historical-character",
                "type": "direct_observation",
                "scope": "profile",
                "summary": (
                    "Zou Ji reinforces the recurring emphasis on composed "
                    "character staging, ornate costume construction, cool "
                    "muted color, and detailed hands and accessories."
                ),
                "reference": (
                    "https://homareworks.blog.fc2.com/blog-entry-77.html"
                ),
            },
        ),
        medium=(
            "polished digital character illustration",
            "commercial card and cover art",
        ),
        genre=(
            "fantasy and science-fiction character key art",
            "historical character illustration",
        ),
        subject_focus=(
            "single character portraits",
            "heroic figures paired with emblematic equipment or machinery",
        ),
        linework=(
            "fine controlled contours",
            "selective textured edge accents",
        ),
        shape_language=(
            "clear figure-led silhouettes",
            "flowing costume shapes contrasted with rigid armor and machinery",
        ),
        facial_design=(
            "refined anime-influenced facial features",
            "focused eyes and restrained expressions",
        ),
        anatomy=(
            "idealized mature proportions",
            "grounded action poses with readable weight",
        ),
        rendering=(
            "polished painterly rendering",
            "careful separation of skin fabric metal and mechanical surfaces",
        ),
        shading=(
            "softly blended form modeling",
            "firm occlusion shadows around layered costume and armor",
        ),
        coloring=(
            "controlled local colors with nuanced material variation",
            "selective luminous accents",
        ),
        palette=(
            "muted jewel tones and cool neutrals",
            "selective warm highlights",
        ),
        lighting=(
            "directional cinematic illumination",
            "subtle rim light and atmospheric glow",
        ),
        composition=(
            "character-centered vertical framing",
            "diagonal action flow and strong silhouette hierarchy",
        ),
        environment=(
            "restrained atmospheric architecture or landscape",
            "graphic or hazy backdrops supporting the figure",
        ),
        clothing=(
            "ornate layered historical and fantasy garments",
            "precisely segmented armor and technical costume details",
        ),
        mood=("dramatic and composed", "heroic or enigmatic"),
        detail_emphasis=(
            "faces and hands",
            "fabric ornament armor materials and mechanical construction",
        ),
    ),
)


_KNOWLEDGE_BASE = KnowledgeBaseLoader(KNOWLEDGE_RECORDS)

# Compatibility snapshot retained for callers that imported ARTISTS directly.
ARTISTS = tuple(
    legacy_artist_view(record)
    for record in _KNOWLEDGE_BASE.published_records()
)


def get_artist(name):
    """Return a defensive copy of a matching record, or None."""
    return _KNOWLEDGE_BASE.get_artist(name)


def list_artists():
    """Return canonical names sorted without case sensitivity."""
    return _KNOWLEDGE_BASE.list_artists()


def get_knowledge_record(name):
    """Return a defensive copy of one published V1.7 knowledge record."""
    return _KNOWLEDGE_BASE.get_knowledge_record(name)


def project_artist_profile(name):
    """Project one published knowledge record into SemanticStyleProfile."""
    record = get_knowledge_record(name)
    return project_semantic_style_profile(record) if record is not None else None


__all__ = [
    "STYLE_PROFILE_FIELDS",
    "KNOWLEDGE_RECORDS",
    "ARTISTS",
    "normalize_artist_name",
    "get_artist",
    "list_artists",
    "get_knowledge_record",
    "project_artist_profile",
]
