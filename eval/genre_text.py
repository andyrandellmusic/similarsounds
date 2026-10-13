"""CLAP text fingerprints for genre descriptions (house styles vs neighbours that slip in: trance,
EDM, techno, pop...). Writes data/clap_genre_text.npz.
    uv run --offline --no-project --python 3.10 --with laion-clap --with "torch<2.6" --with torchvision \
        --with "transformers<4.45" --with "numpy<2" --with "setuptools<70" python -m eval.genre_text"""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
GENRES = {
    # house family
    "house": ["house music", "a house music track with a four on the floor kick", "club house track"],
    "deep house": ["deep house with warm chords and a smooth groove", "deep house track"],
    "tech house": ["tech house with a punchy groove and rolling bassline", "tech house club track"],
    "minimal deep tech": ["minimal deep tech with sparse percussion", "minimal house track"],
    "disco house": ["disco house with funky guitar and strings", "nu disco track"],
    "melodic house": ["melodic house with emotional synths", "progressive house track"],
    "afro house": ["afro house with tribal percussion", "afro house track"],
    # neighbours that shouldn't be in a house catalogue
    "trance": ["trance music", "uplifting trance with big supersaw leads and a long breakdown", "progressive trance track at 138 bpm"],
    "edm": ["big room EDM festival anthem with a huge drop", "commercial electro house drop", "future bass EDM"],
    "techno": ["hard techno", "dark industrial techno", "peak time techno at 135 bpm"],
    "pop": ["a pop song with a singer", "radio pop music", "chart pop ballad"],
    "hip hop": ["hip hop rap song", "trap beat with rap vocals", "r&b slow jam"],
    "dnb dubstep": ["drum and bass", "dubstep with a heavy wobble drop", "jungle breakbeat"],
    "hardstyle": ["hardstyle with distorted kicks", "happy hardcore"],
    "ambient": ["ambient music without drums", "downtempo chill out without a beat"],
    "rock": ["rock band with electric guitars and live drums", "indie rock song"],
}
HOUSE = ["house", "deep house", "tech house", "minimal deep tech", "disco house", "melodic house", "afro house"]


def main():
    import laion_clap, torch
    m = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
    m.load_ckpt(str(Path.home() / ".cache/laion_clap/music_audioset_epoch_15_esc_90.14.pt"))
    names, vecs = [], []
    for g, prompts in GENRES.items():
        with torch.no_grad():
            e = m.get_text_embedding(prompts)
        e = e / np.linalg.norm(e, axis=1, keepdims=True)
        v = e.mean(0); names.append(g); vecs.append(v / np.linalg.norm(v))
    np.savez_compressed(ROOT / "data" / "clap_genre_text.npz", names=np.array(names), emb=np.array(vecs, dtype="float32"),
                        house=np.array(HOUSE))
    print("saved", len(names), "genre descriptions")


if __name__ == "__main__":
    main()
