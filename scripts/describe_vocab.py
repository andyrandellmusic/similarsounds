"""Build the word list for "Describe a sound": every phrase gets a CLAP text fingerprint (same model as the
track fingerprints), saved to data/describe_vocab.npz. The site then matches typed words to these phrases
and phrases to tracks, so it needs no heavy model at run time.

    uv run --no-project --python 3.10 --with laion-clap --with "torch<2.6" --with torchvision \
        python -m scripts.describe_vocab --ckpt ~/.cache/laion_clap/music_audioset_epoch_15_esc_90.14.pt
"""
import argparse, json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

# phrase: words people might type for it (the phrase itself always counts)
VOCAB = {
    # instruments and sounds
    "piano": ["keys", "pianos"], "house piano chords": ["piano chords", "piano stabs"], "rhodes electric piano": ["rhodes", "electric piano", "wurlitzer"],
    "organ": ["organ bass", "hammond"], "saxophone": ["sax", "saxophones"], "trumpet": ["trumpets"], "brass section": ["brass", "horns", "horn"],
    "flute": ["flutes"], "strings": ["string section", "orchestral strings"], "violin": ["violins", "cello"], "harp": [],
    "funky guitar": ["guitar licks", "disco guitar", "wah guitar"], "acoustic guitar": ["acoustic"], "electric guitar": ["guitar", "guitars"],
    "synth lead": ["synth", "synths", "lead synth"], "arpeggiated synth": ["arpeggio", "arpeggios", "arp", "arps"], "warm pads": ["pads", "pad"],
    "plucks": ["pluck", "plucky"], "marimba": ["xylophone", "vibraphone"], "kalimba": ["thumb piano"], "steel drums": ["steel pan"],
    "bells": ["chimes", "bell"], "sitar": [], "oud": [], "choir": ["choirs", "choral"], "bongos and congas": ["bongos", "congas", "conga"],
    "tribal percussion": ["tribal drums", "percussion", "percussive"], "shakers": ["shaker"], "cowbell": [], "claps": ["handclaps", "clap"],
    "crisp hi-hats": ["hi hats", "hihats", "hats"], "big kick drum": ["heavy kick", "punchy kick", "kick"], "breakbeat drums": ["breaks", "breakbeat"],
    "rolling bassline": ["rolling bass", "rolling"], "deep sub bass": ["sub bass", "sub", "subby"], "funky bassline": ["funky bass", "slap bass", "bass guitar"],
    "acid 303 bassline": ["acid", "303", "squelchy"], "wobbly bass": ["wobble", "growly bass"], "chopped vocal samples": ["vocal chops", "chopped vocals", "vocal chop"],
    "vinyl crackle": ["crackle", "vinyl"], "field recordings": ["nature sounds", "birds", "rain sounds", "ocean"],
    # vocals
    "female vocal": ["female vocals", "woman singing", "female singer", "diva"], "male vocal": ["male vocals", "man singing", "male singer"],
    "soulful vocals": ["soulful vocal", "soul vocals"], "gospel vocals": ["gospel"], "spoken word vocal": ["spoken word", "talking", "speech"],
    "rap vocal": ["rap", "rapping", "mc"], "whispered vocals": ["whispers", "whisper", "breathy"], "african vocals": ["african chant", "chants", "chanting"],
    "spanish vocals": ["spanish", "latin vocals"], "instrumental with no vocals": ["instrumental", "no vocals", "no vocal"],
    # mood and feel
    "dark": ["darker", "evil", "menacing"], "moody": ["brooding"], "uplifting": ["uplifting vibe", "positive"], "euphoric": ["euphoria", "hands in the air"],
    "happy": ["feel good", "feelgood", "joyful", "cheerful"], "melancholic": ["sad", "melancholy", "bittersweet"], "emotional": ["emotive", "feelings"],
    "dreamy": ["dream", "ethereal", "floaty", "floating"], "hypnotic": ["trancey", "trance-like", "repetitive"], "groovy": ["groove", "grooves"],
    "funky": ["funk"], "sexy": ["sensual", "seductive"], "chilled": ["chill", "relaxed", "relaxing", "laid back", "laidback", "mellow"],
    "energetic": ["high energy", "upbeat", "lively"], "driving": ["pumping", "relentless"], "aggressive": ["hard", "heavy", "intense"],
    "mysterious": ["mystery", "eerie", "spooky"], "warm": ["warmth", "cosy", "cozy"], "cold": ["icy", "clinical"], "romantic": ["love", "loving"],
    "nostalgic": ["nostalgia", "throwback", "old school", "oldschool"], "cinematic": ["epic", "film score"], "spiritual": ["meditative", "ritual"],
    "psychedelic": ["trippy", "acid trip"], "minimal and stripped back": ["minimal", "stripped back", "sparse", "simple"], "raw": ["gritty", "dirty", "rough"],
    "lo-fi": ["lofi", "lo fi", "dusty"], "jazzy": ["jazz", "jazz chords"], "soulful": ["soul"], "bouncy": ["bounce", "bouncing", "swing", "swingy"],
    # places and times
    "sunset": ["sunset vibes", "golden hour"], "sunrise": ["dawn", "morning"], "summer": ["summery", "sunny", "sunshine"], "beach": ["beach party", "seaside"],
    "late night": ["night", "nighttime", "midnight", "after hours", "afterhours"], "warehouse": ["warehouse party", "rave", "underground"],
    "ibiza": ["balearic", "white isle"], "tropical": ["island", "caribbean"], "rooftop party": ["rooftop", "pool party", "poolside"],
    "rainy day": ["rain", "rainy"], "festival main stage": ["festival", "main stage", "anthem", "anthemic"],
    # styles and eras
    "deep house": ["deep"], "tech house": ["tech"], "minimal deep tech": ["deep tech", "minimal tech"], "afro house": ["afro", "afrobeat", "african"],
    "melodic house": ["melodic", "melodic techno"], "organic house": ["organic", "downtempo"], "progressive house": ["progressive", "prog"],
    "disco house": ["disco", "nu disco", "nu-disco", "french house", "filter house"], "jackin house": ["jackin", "jacking", "chicago"],
    "bass house": ["bassline house", "speed garage"], "soulful house": ["soulful house music"], "acid house": [], "uk garage": ["garage", "ukg", "2 step", "2-step"],
    "latin house": ["latin", "salsa", "brazilian"], "electro": ["electro house"], "techno": ["techno vibes"], "classic 90s house": ["90s", "nineties", "classic house"],
    "80s synth sound": ["80s", "eighties", "retro"], "70s disco": ["70s", "seventies"],
    # energy and use
    "slow and laid-back": ["slow", "slower", "downbeat"], "peak time banger": ["banger", "peak time", "peak-time", "big room"], "warm-up track": ["warm up", "warmup", "opener"],
    "closing track": ["closer", "end of night", "last track"], "big build-up and drop": ["build up", "buildup", "drop", "big drop"], "long breakdown": ["breakdown"],
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ckpt", required=True); args = ap.parse_args()
    import laion_clap, torch
    m = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
    m.load_ckpt(args.ckpt)
    phrases = list(VOCAB)
    vecs = []
    for p in phrases:
        prompts = [f"{p}", f"a house music track with {p}" if not p.endswith("house") else f"a {p} track", f"{p} house music"]
        with torch.no_grad():
            e = m.get_text_embedding(prompts)
        e = e / np.linalg.norm(e, axis=1, keepdims=True)
        v = e.mean(0); vecs.append(v / np.linalg.norm(v))
    np.savez_compressed(ROOT / "data" / "describe_vocab.npz", phrases=np.array(phrases), emb=np.array(vecs, dtype="float32"))
    json.dump({p: s for p, s in VOCAB.items()}, open(ROOT / "data" / "describe_vocab.json", "w"), indent=0)
    print("phrases:", len(phrases))


if __name__ == "__main__":
    main()
