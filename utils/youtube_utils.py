"""
utils/youtube_utils.py
Bulletproof: Works for ANY skill — known or unknown.
Uses YouTube search embed as fallback so videos never show unavailable.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st


# ── Known video library (verified working IDs) ─────────────────────────────────
KNOWN_VIDEOS = {
    "python":            [("rfscVS0vtbw","Python for Beginners – Full Course","freeCodeCamp.org"),
                          ("_uQrJ0TkZlc","Python Full Course for Beginners","Programming with Mosh")],
    "javascript":        [("PkZNo7MFNFg","Learn JavaScript – Full Course","freeCodeCamp.org"),
                          ("W6NZfCO5SIk","JavaScript Tutorial for Beginners","Programming with Mosh")],
    "css":               [("1Rs2ND1ryYc","CSS Full Course for Beginners","freeCodeCamp.org"),
                          ("yfoY53QXEnI","CSS Tutorial – Zero to Hero","freeCodeCamp.org")],
    "html":              [("pQN-pnXPaVg","HTML Full Course – Build a Website","freeCodeCamp.org"),
                          ("kUMe1FH4CHE","HTML Tutorial for Beginners","Programming with Mosh")],
    "react":             [("bMknfKXIFA8","React Course – Beginner's Tutorial","freeCodeCamp.org"),
                          ("SqcY0GlETPk","React Tutorial for Beginners","Programming with Mosh")],
    "machine learning":  [("NWONeJKn6kc","Machine Learning Course for Beginners","freeCodeCamp.org"),
                          ("ukzFI9rgwfU","Machine Learning for Beginners","Microsoft Developer")],
    "deep learning":     [("aircAruvnKk","Neural Networks – 3Blue1Brown","3Blue1Brown"),
                          ("VyWAvY2CF9c","Deep Learning Full Course","Simplilearn")],
    "sql":               [("HXV3zeQKqGY","SQL Tutorial – Full Database Course","freeCodeCamp.org"),
                          ("7S_tz1z_5bA","MySQL Tutorial for Beginners","Programming with Mosh")],
    "docker":            [("fqMOX6JJhGo","Docker Full Course","freeCodeCamp.org"),
                          ("pg19Z8LL06w","Docker Tutorial for Beginners","TechWorld with Nana")],
    "kubernetes":        [("X48VuDVv0do","Kubernetes Tutorial for Beginners","TechWorld with Nana")],
    "git":               [("RGOj5yH7evk","Git and GitHub for Beginners","freeCodeCamp.org"),
                          ("8JJ101D3knE","Git Tutorial for Beginners","Programming with Mosh")],
    "aws":               [("SOTamWqAjkY","AWS Certified Cloud Practitioner","freeCodeCamp.org"),
                          ("k1RI5locZE4","AWS Tutorial For Beginners","Simplilearn")],
    "cloud computing":   [("M988_fsOSWo","Cloud Computing Full Course","freeCodeCamp.org"),
                          ("hnv9jql7LaU","Cloud Computing In 6 Minutes","Simplilearn")],
    "java":              [("eIrMbAQSU34","Java Tutorial for Beginners","Programming with Mosh"),
                          ("A74TOX803D0","Java Full Course","Amigoscode")],
    "c++":               [("vLnPwxZdW4Y","C++ Tutorial for Beginners","freeCodeCamp.org")],
    "typescript":        [("BwuLxPH8IDs","TypeScript Tutorial for Beginners","Programming with Mosh")],
    "nodejs":            [("Oe421EPjeBE","Node.js and Express Full Course","freeCodeCamp.org"),
                          ("TlB_eWDSMt4","Node.js Tutorial for Beginners","Programming with Mosh")],
    "django":            [("F5mRW0jo-U4","Django Full Course","freeCodeCamp.org"),
                          ("rHux0gMZ3Eg","Django Tutorial for Beginners","Programming with Mosh")],
    "flask":             [("Qr4QMBUPxWo","Flask Full Course for Beginners","freeCodeCamp.org")],
    "fastapi":           [("7t2alSnE2-I","FastAPI Tutorial","freeCodeCamp.org")],
    "data science":      [("ua-CiDNNj30","Data Science Full Course","freeCodeCamp.org")],
    "pandas":            [("vmEHCJofslg","Pandas Tutorial","freeCodeCamp.org")],
    "numpy":             [("QUT1VHiLmmI","NumPy Tutorial for Beginners","freeCodeCamp.org")],
    "tensorflow":        [("tPYj3fFJGjk","TensorFlow 2.0 Full Course","freeCodeCamp.org")],
    "pytorch":           [("Z_ikDlimN6A","PyTorch Tutorial for Beginners","Patrick Loeber")],
    "langchain":         [("HSZ_uaif57o","LangChain Full Course","freeCodeCamp.org"),
                          ("lG7Uxts9SXs","LangChain Crash Course","Patrick Loeber")],
    "generative ai":     [("mEsleV16qdo","Generative AI Full Course","Google Cloud Tech")],
    "llm":               [("zjkBMFhNj_g","Large Language Models Explained","3Blue1Brown")],
    "computer vision":   [("oXlwWbU8l2o","OpenCV Python Tutorial","freeCodeCamp.org")],
    "nlp":               [("X2vAabgKiuM","NLP Full Course","freeCodeCamp.org")],
    "system design":     [("i53Gi_K3o7I","System Design Interview","ByteByteGo"),
                          ("F2FmTdLtb_4","System Design Full Course","Gaurav Sen")],
    "algorithms":        [("8hly31xKli0","Data Structures and Algorithms","freeCodeCamp.org")],
    "linux":             [("sWbUDq4S6Y8","Linux Command Line Full Course","freeCodeCamp.org")],
    "devops":            [("j5Zsa_eOXeY","DevOps Tutorial for Beginners","TechWorld with Nana")],
    "terraform":         [("SLB_c_ayRMo","Terraform Tutorial for Beginners","TechWorld with Nana")],
    "mongodb":           [("c2M-rlkkT5o","MongoDB Tutorial for Beginners","Programming with Mosh")],
    "postgresql":        [("qw--VYLpxG4","PostgreSQL Full Course","freeCodeCamp.org")],
    "graphql":           [("ed8SzALpx1k","GraphQL Full Course","freeCodeCamp.org")],
    "microservices":     [("rv4LlmLmVWk","Microservices Tutorial","TechWorld with Nana")],
    "vue":               [("FXpIoQ_rT_c","Vue.js Full Course","freeCodeCamp.org")],
    "angular":           [("3qBXWUpoPHo","Angular Tutorial for Beginners","Programming with Mosh")],
    "flutter":           [("VPvVD8t02U8","Flutter Course – Full Tutorial","freeCodeCamp.org")],
    "kotlin":            [("F9UC9DY-vIU","Kotlin Tutorial for Beginners","freeCodeCamp.org")],
    "rust":              [("BpPEoZX5l3c","Rust Tutorial for Beginners","freeCodeCamp.org")],
    "go":                [("un6ZyFkqFKo","Go Programming – Full Course","freeCodeCamp.org")],
    "blockchain":        [("gyMwXuJrbJQ","Blockchain Full Course","Simplilearn")],
    "cybersecurity":     [("U_P23SqJaDc","Cybersecurity Full Course","freeCodeCamp.org")],
    "power bi":          [("AGrl-H87pRU","Power BI Full Course","freeCodeCamp.org")],
    "tableau":           [("TPMlZxRRaBQ","Tableau Tutorial for Beginners","Simplilearn")],
    "excel":             [("Vl0H-qTclOg","Microsoft Excel Full Course","freeCodeCamp.org")],
    "data structures":   [("8hly31xKli0","Data Structures Full Course","freeCodeCamp.org")],
    "operating system":  [("yK1uBHPdblU","Operating Systems Full Course","freeCodeCamp.org")],
    "networking":        [("qiQR5rTSshw","Computer Networking Full Course","freeCodeCamp.org")],
    "ci/cd":             [("R8_veQiYBjI","CI/CD Pipeline Tutorial","TechWorld with Nana")],
    "redis":             [("XCsS408ye7w","Redis Tutorial","freeCodeCamp.org")],
}

# ── Alias map — maps variations to canonical keys ──────────────────────────────
ALIASES = {
    "js": "javascript", "js tutorial": "javascript",
    "ml": "machine learning", "ai": "generative ai",
    "dl": "deep learning", "nn": "deep learning",
    "k8s": "kubernetes", "kube": "kubernetes",
    "node": "nodejs", "node.js": "nodejs",
    "pg": "postgresql", "postgres": "postgresql",
    "mongo": "mongodb",
    "tf": "tensorflow",
    "genai": "generative ai", "gen ai": "generative ai",
    "cv": "computer vision", "opencv": "computer vision",
    "ds": "data science", "data analysis": "data science",
    "cloud": "cloud computing", "gcp": "cloud computing", "azure": "cloud computing",
    "dsa": "data structures", "data structure": "data structures",
    "os": "operating system",
    "network": "networking", "computer network": "networking",
    "devops": "devops", "dev ops": "devops",
    "infra": "devops", "infrastructure": "devops",
    "iac": "terraform", "infrastructure as code": "terraform",
    "sec": "cybersecurity", "security": "cybersecurity", "ethical hacking": "cybersecurity",
    "ts": "typescript",
    "scss": "css", "sass": "css",
    "html5": "html", "html css": "html",
    "spring": "java", "spring boot": "java",
}


def search_youtube_videos(query: str, max_results: int = 5) -> list:
    """
    Search YouTube.
    Priority: Real API → Known library → YouTube search embed (always works).
    """
    api_key = os.getenv("YOUTUBE_API_KEY") or st.secrets.get("YOUTUBE_API_KEY", "")
    if api_key:
        try:
            from googleapiclient.discovery import build
            youtube = build("youtube", "v3", developerKey=api_key)
            req     = youtube.search().list(
                q=query + " tutorial full course",
                part="snippet", type="video",
                maxResults=max_results,
                videoEmbeddable="true",
            )
            resp    = req.execute()
            results = []
            for item in resp.get("items", []):
                vid_id  = item["id"]["videoId"]
                snippet = item["snippet"]
                results.append({
                    "video_id":    vid_id,
                    "title":       snippet["title"],
                    "description": snippet.get("description",""),
                    "thumbnail":   snippet["thumbnails"]["medium"]["url"],
                    "channel":     snippet["channelTitle"],
                    "url":         f"https://www.youtube.com/watch?v={vid_id}",
                    "embed_url":   f"https://www.youtube.com/embed/{vid_id}",
                    "is_search":   False,
                })
            if results:
                return results
        except Exception:
            pass

    return _smart_match(query, max_results)


def _smart_match(query: str, max_results: int = 5) -> list:
    """
    Smart matching:
    1. Check alias map
    2. Exact key match
    3. Partial key match
    4. Word-level match
    5. ALWAYS fallback to YouTube search embed (never shows unavailable)
    """
    q = query.lower().strip()

    # Step 1: Check aliases
    canonical = ALIASES.get(q)
    if not canonical:
        for alias, canon in ALIASES.items():
            if alias in q:
                canonical = canon
                break

    # Step 2: Use canonical or direct match
    matched_vids = []
    search_key   = canonical or q

    if search_key in KNOWN_VIDEOS:
        matched_vids = KNOWN_VIDEOS[search_key]
    else:
        # Step 3: Partial match — key inside query
        for key, vids in KNOWN_VIDEOS.items():
            if key in q or q in key:
                matched_vids = vids
                break

    # Step 4: Word-level match
    if not matched_vids:
        words = q.split()
        for word in words:
            if len(word) < 3:
                continue
            for key, vids in KNOWN_VIDEOS.items():
                if word in key:
                    matched_vids = vids
                    break
            if matched_vids:
                break

    # Build results from known videos
    results = []
    if matched_vids:
        for vid_id, title, channel in matched_vids[:max_results]:
            results.append({
                "video_id":    vid_id,
                "title":       title,
                "description": f"Learn {query} with this comprehensive tutorial.",
                "thumbnail":   f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg",
                "channel":     channel,
                "url":         f"https://www.youtube.com/watch?v={vid_id}",
                "embed_url":   f"https://www.youtube.com/embed/{vid_id}",
                "is_search":   False,
            })

    # Step 5: ALWAYS add YouTube search embed as extra option (works for ANY skill)
    enc = query.replace(" ", "+")
    results.append({
        "video_id":    f"SEARCH_{enc}",
        "title":       f"🔍 Search YouTube: '{query} tutorial'",
        "description": "Live YouTube search — finds latest videos for this topic.",
        "thumbnail":   "",
        "channel":     "YouTube Search (works for any topic)",
        "url":         f"https://www.youtube.com/results?search_query={enc}+tutorial",
        "embed_url":   f"https://www.youtube.com/embed?listType=search&list={enc}+tutorial",
        "is_search":   True,
    })

    return results[:max_results + 1]


def get_transcript(video_id: str) -> str:
    if not video_id or video_id.startswith("SEARCH_"):
        return ""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item["text"] for item in transcript_list])
        return re.sub(r"\s+", " ", full_text).strip()
    except Exception:
        return ""


def extract_video_id_from_url(url: str):
    match = re.search(r"(?:v=|/embed/|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None


def get_embed_html(video_id: str, width: int = 700, height: int = 394) -> str:
    """Returns embed HTML. Handles search embeds and regular video IDs."""
    if not video_id:
        return ""
    if video_id.startswith("SEARCH_"):
        skill = video_id.replace("SEARCH_", "").replace("+", " ")
        enc   = skill.replace(" ", "+")
        return f"""
        <div style="background:#f8f8f8;border:1px solid #e0e0e0;border-radius:8px;
                    padding:20px;text-align:center;">
            <div style="font-size:1rem;font-weight:600;margin-bottom:12px;">
                🔍 Search YouTube for: <b>{skill}</b>
            </div>
            <a href="https://www.youtube.com/results?search_query={enc}+tutorial"
               target="_blank"
               style="background:#ff0000;color:white;padding:12px 24px;border-radius:8px;
                      text-decoration:none;font-weight:600;font-size:1rem;">
                ▶ Open YouTube Search
            </a>
            <div style="color:#666;font-size:0.8rem;margin-top:12px;">
                Add YOUTUBE_API_KEY in .streamlit/secrets.toml for embedded videos
            </div>
        </div>
        """
    return f"""
    <iframe width="{width}" height="{height}"
        src="https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen style="border-radius:8px;">
    </iframe>
    """
