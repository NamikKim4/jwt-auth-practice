"""'상품등록 및 후기' 게시판에 처음 보여줄 샘플 데이터.

이미지는 외부에서 가져온 게 아니라, 여기서 SVG로 직접 그린 저작권 걱정 없는
간단한 캐릭터 일러스트예요 (base64로 인코딩해서 <img> 태그에 바로 쓸 수 있게 만듦).
"""
import base64

def _svg_to_data_uri(svg: str) -> str:
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _face(cx, cy, r=6):
    """눈 두 개 + 웃는 입 (모든 캐릭터 공통 표정)."""
    return f'''
      <circle cx="{cx-14}" cy="{cy-4}" r="{r}" fill="#222"/>
      <circle cx="{cx+14}" cy="{cy-4}" r="{r}" fill="#222"/>
      <path d="M {cx-16} {cy+14} Q {cx} {cy+30} {cx+16} {cy+14}" stroke="#222" stroke-width="5" fill="none" stroke-linecap="round"/>
    '''

MONGSIL = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="110" r="80" fill="#4d8bf0"/>
  <circle cx="70" cy="70" r="14" fill="#6b9ef5"/>
  {_face(100, 110)}
</svg>'''

ORANGEMON = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <ellipse cx="100" cy="60" rx="10" ry="18" fill="#3ddc84"/>
  <circle cx="100" cy="115" r="75" fill="#f7941d"/>
  {_face(100, 115)}
</svg>'''

KONGKONG = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <ellipse cx="100" cy="110" rx="65" ry="85" fill="#5ec26a"/>
  {_face(100, 110)}
  <ellipse cx="70" cy="180" rx="12" ry="8" fill="#3f9c4c"/>
  <ellipse cx="130" cy="180" rx="12" ry="8" fill="#3f9c4c"/>
</svg>'''

BYUL = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <polygon points="100,15 122,78 190,78 135,118 156,185 100,145 44,185 65,118 10,78 78,78"
    fill="#f4c542"/>
  {_face(100, 105)}
</svg>'''

NEMO = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <rect x="25" y="25" width="150" height="150" rx="34" fill="#9b6bf0"/>
  {_face(100, 100)}
</svg>'''

BEAR = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="55" cy="52" r="24" fill="#8b5e3c"/>
  <circle cx="145" cy="52" r="24" fill="#8b5e3c"/>
  <circle cx="100" cy="115" r="78" fill="#a9744f"/>
  <ellipse cx="100" cy="140" rx="30" ry="22" fill="#d8b48c"/>
  {_face(100, 118)}
</svg>'''

BUNNY = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <ellipse cx="75" cy="35" rx="15" ry="42" fill="#ffe3f0"/>
  <ellipse cx="125" cy="35" rx="15" ry="42" fill="#ffe3f0"/>
  <circle cx="100" cy="118" r="76" fill="#ffffff"/>
  {_face(100, 118)}
  <ellipse cx="100" cy="145" rx="14" ry="10" fill="#ffb6cf"/>
</svg>'''

CAT = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <polygon points="52,58 74,14 92,60" fill="#b0b0b8"/>
  <polygon points="148,58 126,14 108,60" fill="#b0b0b8"/>
  <circle cx="100" cy="118" r="78" fill="#c7c7cf"/>
  {_face(100, 118)}
  <path d="M 82 132 L 56 126 M 82 138 L 54 140 M 118 132 L 144 126 M 118 138 L 146 140"
    stroke="#8a8a92" stroke-width="2.5" stroke-linecap="round"/>
</svg>'''

FOX = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <polygon points="52,52 78,8 92,60" fill="#e8752c"/>
  <polygon points="148,52 122,8 108,60" fill="#e8752c"/>
  <circle cx="100" cy="118" r="78" fill="#f2924a"/>
  <ellipse cx="100" cy="148" rx="36" ry="28" fill="#fff6ec"/>
  {_face(100, 112)}
</svg>'''

PANDA = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="52" cy="48" r="25" fill="#2a2a2a"/>
  <circle cx="148" cy="48" r="25" fill="#2a2a2a"/>
  <circle cx="100" cy="118" r="78" fill="#f7f7f7"/>
  <ellipse cx="80" cy="108" rx="17" ry="21" fill="#2a2a2a"/>
  <ellipse cx="120" cy="108" rx="17" ry="21" fill="#2a2a2a"/>
  {_face(100, 118)}
</svg>'''

PENGUIN = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <ellipse cx="100" cy="115" rx="72" ry="83" fill="#2c3e50"/>
  <ellipse cx="100" cy="132" rx="44" ry="56" fill="#f5f5f5"/>
  <polygon points="91,120 109,120 100,134" fill="#f7941d"/>
  {_face(100, 100)}
</svg>'''

GHOST = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <path d="M 32 188 L 32 100 A 68 68 0 0 1 168 100 L 168 188
    L 148 170 L 128 188 L 108 170 L 92 188 L 72 170 L 52 188 Z" fill="#eaeaf5"/>
  {_face(100, 100)}
</svg>'''

STRAWBERRY = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <path d="M 100 62 C 42 62 26 128 100 184 C 174 128 158 62 100 62 Z" fill="#e8365d"/>
  <polygon points="70,58 100,76 130,58 116,36 100,50 84,36" fill="#4caf50"/>
  {_face(100, 108)}
  <circle cx="72" cy="118" r="3" fill="#ffe082"/>
  <circle cx="128" cy="118" r="3" fill="#ffe082"/>
  <circle cx="60" cy="140" r="3" fill="#ffe082"/>
  <circle cx="140" cy="140" r="3" fill="#ffe082"/>
  <circle cx="100" cy="150" r="3" fill="#ffe082"/>
  <circle cx="80" cy="165" r="3" fill="#ffe082"/>
  <circle cx="120" cy="165" r="3" fill="#ffe082"/>
</svg>'''

LADYBUG = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="122" r="76" fill="#e8365d"/>
  <line x1="100" y1="46" x2="100" y2="198" stroke="#2a2a2a" stroke-width="4"/>
  <ellipse cx="100" cy="55" rx="46" ry="34" fill="#2a2a2a"/>
  {_face(100, 118)}
  <circle cx="70" cy="128" r="9" fill="#2a2a2a"/>
  <circle cx="130" cy="128" r="9" fill="#2a2a2a"/>
  <circle cx="100" cy="160" r="9" fill="#2a2a2a"/>
</svg>'''

BEE = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <ellipse cx="65" cy="85" rx="30" ry="22" fill="#ffffff" opacity="0.85"/>
  <ellipse cx="135" cy="85" rx="30" ry="22" fill="#ffffff" opacity="0.85"/>
  <ellipse cx="100" cy="120" rx="70" ry="60" fill="#f4c542"/>
  <rect x="30" y="98" width="140" height="20" fill="#2a2a2a"/>
  <rect x="30" y="135" width="140" height="18" fill="#2a2a2a"/>
  {_face(100, 108)}
</svg>'''

DOG = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <ellipse cx="48" cy="90" rx="24" ry="42" fill="#c9a06a" transform="rotate(-15 48 90)"/>
  <ellipse cx="152" cy="90" rx="24" ry="42" fill="#c9a06a" transform="rotate(15 152 90)"/>
  <circle cx="100" cy="118" r="78" fill="#e8c896"/>
  <ellipse cx="100" cy="150" rx="30" ry="22" fill="#fff6e8"/>
  {_face(100, 112)}
  <ellipse cx="100" cy="132" rx="8" ry="6" fill="#4a3423"/>
</svg>'''

CHICK = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="118" r="78" fill="#f9d94e"/>
  <polygon points="88,120 112,120 100,136" fill="#f7941d"/>
  <path d="M 60 55 Q 75 30 95 50" stroke="#f9d94e" stroke-width="10" fill="none" stroke-linecap="round"/>
  {_face(100, 105)}
</svg>'''

DUCK = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="118" r="78" fill="#fff1b8"/>
  <ellipse cx="100" cy="140" rx="38" ry="18" fill="#f7941d"/>
  {_face(100, 105)}
</svg>'''

SQUIRREL = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <path d="M 150 60 C 210 60 210 160 140 175 C 190 130 175 75 150 60 Z" fill="#a9744f"/>
  <circle cx="90" cy="120" r="66" fill="#c68a54"/>
  {_face(90, 118)}
  <ellipse cx="90" cy="148" rx="24" ry="16" fill="#f0d3ab"/>
</svg>'''

HIPPO = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="52" cy="60" r="16" fill="#b98fc7"/>
  <circle cx="148" cy="60" r="16" fill="#b98fc7"/>
  <circle cx="100" cy="120" r="80" fill="#c9a2d6"/>
  <circle cx="65" cy="130" r="14" fill="#f2b6c9" opacity="0.7"/>
  <circle cx="135" cy="130" r="14" fill="#f2b6c9" opacity="0.7"/>
  {_face(100, 118)}
</svg>'''

TIGER = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="52" cy="52" r="20" fill="#e8752c"/>
  <circle cx="148" cy="52" r="20" fill="#e8752c"/>
  <circle cx="100" cy="118" r="78" fill="#f2924a"/>
  <path d="M 45 90 Q 65 80 80 95 M 40 115 Q 62 108 78 120 M 120 95 Q 135 80 155 90 M 122 120 Q 138 108 160 115"
    stroke="#2a2a2a" stroke-width="6" fill="none" stroke-linecap="round"/>
  {_face(100, 115)}
</svg>'''

LION = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="118" r="92" fill="#c9782e"/>
  <circle cx="100" cy="118" r="66" fill="#f4c542"/>
  {_face(100, 118)}
</svg>'''

KOALA = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="42" cy="90" r="34" fill="#aeb4bd"/>
  <circle cx="158" cy="90" r="34" fill="#aeb4bd"/>
  <circle cx="100" cy="118" r="76" fill="#c3c9d1"/>
  <ellipse cx="100" cy="128" rx="22" ry="16" fill="#5a5f66"/>
  {_face(100, 110)}
</svg>'''

FISH = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <polygon points="165,110 198,82 198,138" fill="#4d8bf0"/>
  <ellipse cx="100" cy="110" rx="80" ry="60" fill="#6b9ef5"/>
  <path d="M 60 90 Q 80 70 100 90" stroke="#3d78d8" stroke-width="6" fill="none" stroke-linecap="round"/>
  {_face(85, 105)}
</svg>'''

OCTOPUS = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <path d="M 30 110 A 70 70 0 0 1 170 110 L 170 150 L 30 150 Z" fill="#c77dd6"/>
  <path d="M 40 150 Q 40 175 30 185 M 65 150 Q 65 178 55 190 M 90 150 Q 90 180 90 195
    M 110 150 Q 110 180 110 195 M 135 150 Q 135 178 145 190 M 160 150 Q 160 175 170 185"
    stroke="#c77dd6" stroke-width="14" fill="none" stroke-linecap="round"/>
  {_face(100, 115)}
</svg>'''

JELLYFISH = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <path d="M 35 100 A 65 65 0 0 1 165 100 Z" fill="#f2a6d0"/>
  <path d="M 50 100 Q 50 140 40 175 M 80 100 Q 80 145 75 185 M 110 100 Q 110 145 115 185
    M 140 100 Q 140 140 150 175"
    stroke="#f2a6d0" stroke-width="8" fill="none" stroke-linecap="round"/>
  {_face(100, 90)}
</svg>'''

SNOWMAN = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="140" r="54" fill="#ffffff"/>
  <circle cx="100" cy="66" r="38" fill="#ffffff"/>
  <polygon points="100,66 130,72 100,78" fill="#f7941d"/>
  <circle cx="100" cy="120" r="5" fill="#2a2a2a"/>
  <circle cx="100" cy="145" r="5" fill="#2a2a2a"/>
  <circle cx="100" cy="170" r="5" fill="#2a2a2a"/>
  {_face(100, 58, r=5)}
</svg>'''

CACTUS = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <polygon points="60,190 140,190 130,150 70,150" fill="#a9744f"/>
  <rect x="80" y="60" width="40" height="110" rx="20" fill="#5ec26a"/>
  <path d="M 80 100 Q 40 100 40 70 Q 40 55 55 55 L 55 90 Q 55 100 80 100 Z" fill="#5ec26a"/>
  <path d="M 120 120 Q 160 120 160 95 Q 160 82 148 82 L 148 112 Q 148 120 120 120 Z" fill="#5ec26a"/>
  {_face(100, 90, r=5)}
</svg>'''

MUSHROOM = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <rect x="78" y="110" width="44" height="70" rx="16" fill="#fdf1de"/>
  <path d="M 20 110 A 80 70 0 0 1 180 110 Z" fill="#e8365d"/>
  <circle cx="60" cy="80" r="9" fill="#ffffff"/>
  <circle cx="100" cy="60" r="10" fill="#ffffff"/>
  <circle cx="140" cy="82" r="8" fill="#ffffff"/>
  {_face(100, 130, r=5)}
</svg>'''

CLOUD = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="65" cy="120" r="38" fill="#eef1fb"/>
  <circle cx="120" cy="105" r="46" fill="#eef1fb"/>
  <circle cx="150" cy="130" r="32" fill="#eef1fb"/>
  <rect x="50" y="120" width="120" height="45" rx="22" fill="#eef1fb"/>
  {_face(105, 120)}
</svg>'''

SEED_PRODUCTS = [
    {
        "name": "몽실이",
        "description": "동글동글 파란 몽실이예요. 만지면 말랑말랑할 것 같은 느낌적인 느낌! 오늘 처음 데려왔는데 벌써 정들었어요 :)",
        "svg": MONGSIL,
    },
    {
        "name": "오렌지몬",
        "description": "상큼한 오렌지색 친구, 오렌지몬! 머리 위에 초록 잎사귀가 매력 포인트예요. 볼 때마다 기분이 좋아져요.",
        "svg": ORANGEMON,
    },
    {
        "name": "콩콩이",
        "description": "길쭉한 몸매의 콩콩이. 짧은 다리로 콩콩 뛰어다니는 상상을 하니 너무 귀여워요. 초록색이라 눈이 편안해요.",
        "svg": KONGKONG,
    },
    {
        "name": "별이",
        "description": "밤하늘에서 내려온 노란 별이. 반짝반짝 빛나는 별 모양이 책상 위에 있으니까 분위기가 확 살아나요.",
        "svg": BYUL,
    },
    {
        "name": "네모",
        "description": "각지지만 왠지 정감 가는 보라색 네모. 모서리가 둥글게 처리돼있어서 부딪혀도 안 아플 것 같아요. 제일 차분한 성격일 듯.",
        "svg": NEMO,
    },
    {
        "name": "곰돌이",
        "description": "포근한 갈색 곰돌이예요. 통통한 몸이랑 동그란 귀 보면 저절로 안아주고 싶어져요. 옆에 두면 마음이 편안해지는 친구예요.",
        "svg": BEAR,
    },
    {
        "name": "토순이",
        "description": "쫑긋한 귀가 매력 포인트인 하얀 토순이. 볼 때마다 코 앞에 당근 하나 그려주고 싶어져요. 순백색이라 어디에 둬도 깔끔해요.",
        "svg": BUNNY,
    },
    {
        "name": "냥이",
        "description": "새침한 표정의 회색 냥이. 수염까지 그려놓으니까 진짜 고양이 같아요. 도도한데 은근 귀여운 매력 있어요.",
        "svg": CAT,
    },
    {
        "name": "여우",
        "description": "쫑긋 세모 귀에 하얀 배가 포인트인 여우예요. 주황색이 화사해서 책상 위 분위기 메이커 역할 톡톡히 해요.",
        "svg": FOX,
    },
    {
        "name": "판다",
        "description": "까만 눈 주위랑 귀가 매력적인 판다예요. 흑백 조합이라 어떤 컬러랑 놔도 잘 어울려요. 볼 때마다 힐링돼요.",
        "svg": PANDA,
    },
    {
        "name": "펭귄",
        "description": "뒤뚱뒤뚱 걸어다닐 것 같은 펭귄이에요. 남색이랑 흰색 배가 딱 떨어지게 나뉘어서 깔끔해 보여요. 주황색 부리가 킥이에요.",
        "svg": PENGUIN,
    },
    {
        "name": "유령이",
        "description": "무섭지 않고 순둥순둥한 유령이예요. 아래쪽 물결 모양이 하늘하늘한 느낌이라 귀엽기만 해요. 밤에 봐도 하나도 안 무서워요.",
        "svg": GHOST,
    },
    {
        "name": "딸기",
        "description": "씨앗까지 콕콕 박힌 빨간 딸기예요. 초록 꼭지가 포인트라 진짜 과일처럼 상큼해 보여요. 보기만 해도 새콤달콤한 기분이 들어요.",
        "svg": STRAWBERRY,
    },
    {
        "name": "무당벌레",
        "description": "동글동글 빨간 등에 검은 점이 콕콕 박힌 무당벌레예요. 작고 야무진 느낌이라 볼 때마다 기분이 좋아져요.",
        "svg": LADYBUG,
    },
    {
        "name": "꿀벌이",
        "description": "노랑 검정 줄무늬가 선명한 꿀벌이예요. 투명한 날개 두 장이 진짜 날아갈 것처럼 그려져 있어요. 부지런한 느낌이라 마음에 들어요.",
        "svg": BEE,
    },
    {
        "name": "강아지",
        "description": "귀가 축 늘어진 순한 강아지예요. 코 색깔까지 신경 써서 그렸더니 훨씬 사실적으로 보여요. 만지면 복슬복슬할 것 같아요.",
        "svg": DOG,
    },
    {
        "name": "병아리",
        "description": "삐약삐약 소리가 들릴 것 같은 노란 병아리. 머리 위 작은 깃털이 포인트예요. 보고만 있어도 기운이 나요.",
        "svg": CHICK,
    },
    {
        "name": "오리",
        "description": "동글넓적한 주황 부리가 매력인 오리예요. 연노랑 색이라 병아리랑은 또 다른 느낌으로 사랑스러워요.",
        "svg": DUCK,
    },
    {
        "name": "다람쥐",
        "description": "풍성한 꼬리가 진짜 매력 포인트인 다람쥐예요. 도토리 하나 쥐여주고 싶은 비주얼이에요. 볼주머니도 통통해 보여요.",
        "svg": SQUIRREL,
    },
    {
        "name": "하마",
        "description": "볼터치까지 그려 넣은 발그레한 하마예요. 보라색이라 흔치 않은 컬러인데 은근 잘 어울려요. 순한 인상이 매력이에요.",
        "svg": HIPPO,
    },
    {
        "name": "호랑이",
        "description": "줄무늬까지 꼼꼼하게 그린 아기 호랑이예요. 무섭기보단 귀엽고 씩씩한 느낌이에요. 주황빛이 눈에 확 띄어요.",
        "svg": TIGER,
    },
    {
        "name": "사자",
        "description": "풍성한 갈기가 왕관처럼 둘러진 사자예요. 노랑이랑 갈색 조합이 따뜻한 느낌을 줘요. 볼 때마다 든든한 기분이 들어요.",
        "svg": LION,
    },
    {
        "name": "코알라",
        "description": "큼직한 귀가 포인트인 코알라예요. 회색 톤이라 차분하고 잔잔한 매력이 있어요. 나무에 매달려 있을 것만 같아요.",
        "svg": KOALA,
    },
    {
        "name": "물고기",
        "description": "지느러미랑 꼬리까지 야무지게 그린 파란 물고기예요. 헤엄치는 모습이 상상돼서 볼 때마다 시원해지는 느낌이에요.",
        "svg": FISH,
    },
    {
        "name": "문어",
        "description": "다리 여덟 개를 최대한 살려서 그린 보라색 문어예요. 물결치는 다리 모양이 은근 귀여워요. 색이 화사해서 눈에 잘 띄어요.",
        "svg": OCTOPUS,
    },
    {
        "name": "해파리",
        "description": "하늘하늘한 촉수가 매력인 분홍 해파리예요. 바닷속에서 둥둥 떠다니는 모습이 상상돼서 마음이 편안해져요.",
        "svg": JELLYFISH,
    },
    {
        "name": "눈사람",
        "description": "당근 코까지 완벽한 눈사람이에요. 겨울 느낌 물씬 나서 볼 때마다 포근해져요. 단추 세 개도 야무지게 박아 넣었어요.",
        "svg": SNOWMAN,
    },
    {
        "name": "선인장",
        "description": "화분에 담긴 초록 선인장이에요. 양쪽으로 뻗은 팔 모양이 인사하는 것 같아서 볼 때마다 웃음이 나요. 물 안 줘도 되니까 관리도 편해요(?)",
        "svg": CACTUS,
    },
    {
        "name": "버섯",
        "description": "동글동글 하얀 점이 콕콕 박힌 빨간 버섯이에요. 동화 속에서 튀어나온 것 같은 비주얼이라 볼 때마다 기분 좋아져요.",
        "svg": MUSHROOM,
    },
    {
        "name": "구름이",
        "description": "몽글몽글 뭉게뭉게, 하늘에 떠있는 구름이예요. 연한 하늘색 배경이라 어디에 둬도 편안한 느낌을 줘요. 보고 있으면 마음이 차분해져요.",
        "svg": CLOUD,
    },
]


def seed_products():
    """products 테이블에 아직 없는 샘플 캐릭터만 골라서 등록한다 (이름 기준, 중복 방지)."""
    from repositories.products import list_products, create_product

    existing_names = {p["name"] for p in list_products()}

    for item in SEED_PRODUCTS:
        if item["name"] in existing_names:
            continue
        create_product(
            author="관리자",
            name=item["name"],
            description=item["description"],
            image_data=_svg_to_data_uri(item["svg"]),
        )
