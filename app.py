import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="FC 27 WebGL Stadium Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SIDEBAR: MATCH & PHYSICS ENGINE SETTINGS ---
with st.sidebar:
    st.title("⚽ FC 27 Engine Deck")
    st.caption("Configure live stadium atmosphere, AI difficulty & ball aerodynamics.")

    stadium_time = st.selectbox(
        "Stadium Lighting",
        ["Champions Night (Floodlights)", "Golden Sunset", "Overcast Daylight"],
        index=0,
    )
    gk_difficulty = st.select_slider(
        "Goalkeeper AI Rating",
        options=["Amateur (65)", "Semi-Pro (75)", "World Class (86)", "Legendary (94)"],
        value="World Class (86)",
    )
    curve_power = st.slider(
        "Magnus Spin Sensitivity",
        min_value=0.5,
        max_value=2.5,
        value=1.4,
        step=0.1,
    )
    pitch_speed = st.slider(
        "Grass Wetness / Ball Glide",
        min_value=0.92,
        max_value=0.99,
        value=0.96,
        step=0.01,
    )

    st.divider()
    st.markdown(
        """
        **🎮 Pitch Controls (Click inside stadium first):**
        * **W A S D / Arrows:** Dribble & Sprint (**Shift**)
        * **Hold Spacebar:** Charge Power Shot
        * **Hold Q or E while shooting:** Finesse Curve Left / Right
        * **T:** Driven Through-Ball Pass
        * **R:** Reset Ball & Striker
        """
    )

# Map Streamlit controls to engine parameters
sky_colors = {
    "Champions Night (Floodlights)": ("#070d19", "#dbeafe", 1.15),
    "Golden Sunset": ("#2b142c", "#fdba74", 1.25),
    "Overcast Daylight": ("#334155", "#f8fafc", 1.35),
}
bg_hex, light_hex, light_int = sky_colors[stadium_time]

gk_speeds = {
    "Amateur (65)": 2.4,
    "Semi-Pro (75)": 3.8,
    "World Class (86)": 5.2,
    "Legendary (94)": 7.0,
}
gk_react = gk_speeds[gk_difficulty]

st.title("⚽ Next-Gen 3D Football Stadium Engine")
st.caption(f"Mode: **{stadium_time}** • Keeper AI: **{gk_difficulty}** • Click inside the pitch to play")

# --- EMBEDDED 3D THREE.JS FOOTBALL ENGINE ---
game_html = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }}
    body {{ overflow: hidden; background: {bg_hex}; color: #fff; user-select: none; }}
    #hud-top {{
      position: absolute; top: 16px; left: 16px; right: 16px;
      display: flex; justify-content: space-between; align-items: center; pointer-events: none;
    }}
    .broadcast-bug {{
      display: flex; align-items: center; background: rgba(15, 23, 42, 0.9);
      border: 1px solid #38bdf8; border-radius: 8px; overflow: hidden; font-weight: 800; font-size: 16px;
    }}
    .team-home {{ background: #1d4ed8; padding: 8px 14px; }}
    .score-box {{ padding: 8px 16px; background: #0f172a; color: #facc15; font-size: 18px; }}
    .team-away {{ background: #b91c1c; padding: 8px 14px; }}
    .telemetry {{
      background: rgba(15, 23, 42, 0.85); border: 1px solid #334155;
      padding: 8px 16px; border-radius: 8px; font-size: 13px; color: #e2e8f0;
    }}
    #power-wrap {{
      position: absolute; bottom: 22px; left: 50%; transform: translateX(-50%);
      width: 260px; text-align: center; pointer-events: none;
    }}
    #power-label {{ font-size: 11px; font-weight: 700; letter-spacing: 1px; margin-bottom: 4px; color: #cbd5e1; }}
    #power-track {{
      width: 100%; height: 12px; background: rgba(255,255,255,0.18);
      border-radius: 6px; overflow: hidden; border: 1px solid rgba(255,255,255,0.25);
    }}
    #power-fill {{ width: 0%; height: 100%; background: linear-gradient(90deg, #22c55e, #eab308, #ef4444); }}
    #goal-banner {{
      position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%);
      font-size: 64px; font-weight: 900; color: #facc15;
      text-shadow: 0 6px 28px rgba(0,0,0,0.9); display: none; pointer-events: none;
    }}
    #focus-tip {{
      position: absolute; bottom: 22px; right: 20px;
      background: rgba(15, 23, 42, 0.8); padding: 6px 12px; border-radius: 6px; font-size: 12px; color: #94a3b8;
    }}
  </style>
</head>
<body>
  <div id="hud-top">
    <div class="broadcast-bug">
      <div class="team-home">FC ATLAS</div>
      <div class="score-box"><span id="s-home">0</span> - <span id="s-away">0</span></div>
      <div class="team-away">REAL AI</div>
    </div>
    <div class="telemetry">
      Shot Speed: <b id="tel-speed">0 km/h</b> &nbsp;|&nbsp; Spin: <b id="tel-spin">None</b> &nbsp;|&nbsp; Shots: <b id="tel-shots">0</b>
    </div>
  </div>

  <div id="goal-banner">GOOOAL!</div>

  <div id="power-wrap">
    <div id="power-label">SHOT POWER</div>
    <div id="power-track"><div id="power-fill"></div></div>
  </div>

  <div id="focus-tip">Click pitch to activate keyboard controls</div>

  <script src="https://cloudflare.com"></script>
  <script>
    const CURVE_MULT = {curve_power};
    const FRICTION = {pitch_speed};
    const GK_SPEED = {gk_react};

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("{bg_hex}");
    scene.fog = new THREE.Fog("{bg_hex}", 70, 185);

    const camera = new THREE.PerspectiveCamera(46, window.innerWidth / window.innerHeight, 0.1, 320);
    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    document.body.appendChild(renderer.domElement);

    // Stadium Lighting
    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const floodlight = new THREE.DirectionalLight("{light_hex}", {light_int});
    floodlight.position.set(30, 50, 25);
    floodlight.castShadow = true;
    floodlight.shadow.mapSize.width = 2048;
    floodlight.shadow.mapSize.height = 2048;
    scene.add(floodlight);

    // Striped Stadium Pitch
    const pitchGroup = new THREE.Group();
    const stripeCount = 14;
    const stripeDepth = 105 / stripeCount;
    for (let i = 0; i < stripeCount; i++) {{
      const mat = new THREE.MeshStandardMaterial({{
        color: i % 2 === 0 ? 0x15803d : 0x166534,
        roughness: 0.85
      }});
      const strip = new THREE.Mesh(new THREE.PlaneGeometry(68, stripeDepth), mat);
      strip.rotation.x = -Math.PI / 2;
      strip.position.z = -52.5 + stripeDepth * (i + 0.5);
      strip.receiveShadow = true;
      pitchGroup.add(strip);
    }}
    scene.add(pitchGroup);

    // Stadium Stands (3D Bowl Backdrop)
    const standMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.9 }});
    const northStand = new THREE.Mesh(new THREE.BoxGeometry(84, 14, 12), standMat);
    northStand.position.set(0, 7, -64);
    const westStand = new THREE.Mesh(new THREE.BoxGeometry(12, 14, 120), standMat);
    westStand.position.set(-44, 7, 0);
    const eastStand = new THREE.Mesh(new THREE.BoxGeometry(12, 14, 120), standMat);
    eastStand.position.set(44, 7, 0);
    scene.add(northStand, westStand, eastStand);

    // Pitch Markings & Penalty Box
    const lineMat = new THREE.LineBasicMaterial({{ color: 0xffffff }});
    function addRect(w, d, zCenter) {{
      const hw = w / 2, hd = d / 2;
      const pts = [
        new THREE.Vector3(-hw, 0.04, zCenter - hd),
        new THREE.Vector3(hw, 0.04, zCenter - hd),
        new THREE.Vector3(hw, 0.04, zCenter + hd),
        new THREE.Vector3(-hw, 0.04, zCenter + hd),
        new THREE.Vector3(-hw, 0.04, zCenter - hd)
      ];
      scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), lineMat));
    }}
    addRect(68, 105, 0);
    addRect(40.3, 16.5, -44.25);

    // Goal Frame & Netting
    const postMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, metalness: 0.3, roughness: 0.2 }});
    const leftPost = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 2.6), postMat);
    leftPost.position.set(-4.2, 1.3, -52.5);
    const rightPost = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 2.6), postMat);
    rightPost.position.set(4.2, 1.3, -52.5);
    const crossbar = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 8.54), postMat);
    crossbar.rotation.z = Math.PI / 2;
    crossbar.position.set(0, 2.6, -52.5);
    const netMat = new THREE.MeshBasicMaterial({{ color: 0xe2e8f0, wireframe: true, transparent: true, opacity: 0.35 }});
    const netBox = new THREE.Mesh(new THREE.BoxGeometry(8.4, 2.6, 2.2), netMat);
    netBox.position.set(0, 1.3, -53.6);
    scene.add(leftPost, rightPost, crossbar, netBox);

    // Striker, Defender & Goalkeeper
    function createAthlete(hexColor, x, z) {{
      const mesh = new THREE.Mesh(
        new THREE.CapsuleGeometry(0.45, 1.1, 8, 16),
        new THREE.MeshStandardMaterial({{ color: hexColor, roughness: 0.4 }})
      );
      mesh.position.set(x, 1.0, z);
      mesh.castShadow = true;
      scene.add(mesh);
      return mesh;
    }}

    const striker = createAthlete(0x2563eb, 0, -16);
    const defender = createAthlete(0xdc2626, 2.5, -34);
    const keeper = createAthlete(0xf59e0b, 0, -51.5);

    // 3D Match Ball
    const ball = new THREE.Mesh(
      new THREE.SphereGeometry(0.32, 24, 24),
      new THREE.MeshStandardMaterial({{ color: 0xffffff, roughness: 0.35 }})
    );
    ball.castShadow = true;
    scene.add(ball);

    let ballPos = new THREE.Vector3(0, 0.32, -18);
    let ballVel = new THREE.Vector3(0, 0, 0);
    let ballSpin = 0;
    let power = 0;
    let charging = false;
    let goals = 0;
    let shots = 0;
    const keys = {{}};

    function resetPlay() {{
      striker.position.set((Math.random() - 0.5) * 14, 1.0, -16);
      defender.position.set((Math.random() - 0.5) * 10, 1.0, -34);
      ballPos.set(striker.position.x, 0.32, striker.position.z - 2.0);
      ballVel.set(0, 0, 0);
      ballSpin = 0;
    }}

