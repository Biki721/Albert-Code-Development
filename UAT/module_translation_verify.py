import fasttext
from moduletranslation_phase4 import translation_errors, translation_errors_prob, postprocess

# Load the same model your module is using
model = fasttext.load_model("lid.176.bin")

# Some example texts in different languages
samples = {
    "en": "This is an English sentence about servers and networking.",
    "fr": "Ceci est une phrase française sur les serveurs et le réseau.",
    "de": "Dies ist ein deutscher Satz über Server und Netzwerke.",
    "es": "Esta es una frase en español sobre servidores y redes.",
    "it": "Questa è una frase italiana sui server e le reti.",
    "pt": "Esta é uma frase em português sobre servidores e redes.",
    "ru": "Это русское предложение о серверах и сетях.",
    "zh": "这是一句关于服务器和网络的中文句子。",
    "ja": "これはサーバーとネットワークについての日本語の文です。",
    "ko": "이것은 서버와 네트워크에 대한 한국어 문장입니다.",
}

for true_code, text in samples.items():
    labels, probs = model.predict(text, k=3, threshold=0.0)
    # Convert labels like '__label__en' to 'en'
    pred_langs = [lbl.split("__")[-1] for lbl in labels]

    print(f"True: {true_code:2} | Text: {text}")
    print("Predicted:", list(zip(pred_langs, [round(p, 4) for p in probs])))
    print("-" * 80)

print()
print("=== Testing full translation_errors pipeline (target: French) ===")

extracted_text = [
    "Ceci est une page de test pour la détection de langue.",
    "Ce produit prend en charge la configuration avancée.",
    "This paragraph is accidentally left in English.",
    "Dieses Segment ist auf Deutsch und sollte ein Fehler sein.",
    "Serveurs HPE ProLiant Gen10",
]

tbi = [
    "Hewlett Packard Enterprise",
    "Accueil",
    "Connexion",
]

articletitles = [
    "Guide de configuration rapide",
    "Quick configuration guide",
]

errors = translation_errors(extracted_text, tbi, articletitles, "French")

print()
print("Detected potential translation issues:")
for e in errors:
    print("-", repr(e))

print()
print("=== Single-snippet sanity test (target: French) ===")

test_snippets = [
    "Veuillez mettre à jour la configuration du serveur.",
    "Please update the server configuration immediately.",
    "Dies ist ein deutscher Test für die Spracheerkennung.",
]

errors_single = translation_errors(test_snippets, [], [], "French")

print()
print("Input snippets and whether they were flagged:")
for s in test_snippets:
    normalized = postprocess(s)
    flagged = normalized in errors_single
    print("-", repr(s), "->", "FLAGGED" if flagged else "OK")

print()
print("Raw errors_single list:", errors_single)

print()
print("=== Asian language hard-word test (raw FastText) ===")

asian_hard_samples = {
    "zh": [
        "存储阵列的高可用性配置示例：HPE Alletra 6000 集群。",
        "请使用 iLO 管理接口更新固件版本 v3.21。",
    ],
    "ja": [
        "この手順では、HPE ProLiant サーバーのファームウェアをオンラインで更新します。",
        "障害が発生したノードをクラスタから安全に切り離してください。",
    ],
    "ko": [
        "이 가이드는 HPE ProLiant 서버의 펌웨어 업그레이드 절차를 설명합니다.",
        "장애 조치 클러스터에서 장애가 발생한 노드를 격리하십시오.",
    ],
}

for lang_code, texts in asian_hard_samples.items():
    print()
    print(f"-- Samples for {lang_code} --")
    for text in texts:
        labels, probs = model.predict(text, k=3, threshold=0.0)
        pred_langs = [lbl.split("__")[-1] for lbl in labels]
        print("Text:", text)
        print("Predicted:", list(zip(pred_langs, [round(p, 4) for p in probs])))

print()
print("=== Asian language hard-word test (translation_errors) ===")

asian_configs = [
    ("Chinese", asian_hard_samples["zh"] + ["This is English text inside a Chinese page."]),
    ("Japanese", asian_hard_samples["ja"] + ["This is English text inside a Japanese page."]),
    ("Korean", asian_hard_samples["ko"] + ["This is English text inside a Korean page."]),
]

for lang_name, snippets in asian_configs:
    print()
    print(f"Target language: {lang_name}")
    try:
        errs_basic = translation_errors(snippets, [], [], lang_name)
        errs_prob = translation_errors_prob(snippets, [], [], lang_name)
        print("Input snippets:")
        for s in snippets:
            print("-", repr(s))
        print("Detected issues (basic):")
        for e in errs_basic:
            print("-", repr(e))
        if not errs_basic:
            print("(none)")
        print("Detected issues (probabilistic):")
        for e in errs_prob:
            print("-", repr(e))
        if not errs_prob:
            print("(none)")
    except Exception as exc:
        print("Error while running translation_errors for", lang_name, ":", exc)

print()
print("=== Cross-language thorough test for translation_errors_prob ===")

codes_verify = {
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Chinese': 'zh-cn',
    'Russian': 'ru',
    'Portugese': 'pt',
    'Indonesian': 'id',
    'Singaporean': 'en',
    'Korean': 'ko',
    'Turkish': 'tr',
    'Japanese': 'ja',
    'Taiwan': 'zh-tw',
    'Spanish': 'es',
    'LARSpanish': 'es',
    'English': 'en',
}

all_lang_samples = {
    'en': [
        "This is an English configuration guide for HPE ProLiant servers.",
        "Use this wizard to configure network interfaces on HPE servers.",
        "Review the firmware release notes before applying any updates.",
    ],
    'fr': [
        "Ce guide explique la configuration avancée des serveurs HPE.",
        "Utilisez cet assistant pour configurer les interfaces réseau sur vos serveurs HPE.",
        "Lisez attentivement les notes de version du microprogramme avant toute mise à jour.",
    ],
    'de': [
        "Dieses Handbuch beschreibt die erweiterte Konfiguration von HPE Servern.",
        "Verwenden Sie diesen Assistenten, um Netzwerkschnittstellen auf HPE Servern zu konfigurieren.",
        "Lesen Sie die Firmware-Versionshinweise sorgfältig, bevor Sie ein Update durchführen.",
    ],
    'it': [
        "Questa guida descrive la configurazione avanzata dei server HPE.",
        "Utilizzare questa procedura guidata per configurare le interfacce di rete sui server HPE.",
        "Leggere attentamente le note di rilascio del firmware prima di eseguire qualsiasi aggiornamento.",
    ],
    'es': [
        "Esta guía describe la configuración avanzada de los servidores HPE.",
        "Use este asistente para configurar las interfaces de red en los servidores HPE.",
        "Lea detenidamente las notas de la versión del firmware antes de realizar cualquier actualización.",
    ],
    'pt': [
        "Este guia descreve a configuração avançada dos servidores HPE.",
        "Use este assistente para configurar as interfaces de rede nos servidores HPE.",
        "Leia atentamente as notas de versão do firmware antes de aplicar qualquer atualização.",
    ],
    'ru': [
        "В этом руководстве описывается расширенная конфигурация серверов HPE.",
        "Используйте этот мастер для настройки сетевых интерфейсов на серверах HPE.",
        "Внимательно прочитайте примечания к выпуску прошивки перед установкой обновлений.",
    ],
    'id': [
        "Panduan ini menjelaskan konfigurasi lanjutan untuk server HPE.",
        "Gunakan wizard ini untuk mengonfigurasi antarmuka jaringan pada server HPE.",
        "Harap tinjau catatan rilis firmware sebelum menerapkan pembaruan apa pun.",
    ],
    'tr': [
        "Bu kılavuz, HPE sunucularının gelişmiş yapılandırmasını açıklar.",
        "HPE sunucularında ağ arabirimlerini yapılandırmak için bu sihirbazı kullanın.",
        "Herhangi bir güncelleme uygulamadan önce firmware sürüm notlarını dikkatlice inceleyin.",
    ],
    'zh-cn': [
        "本指南说明了 HPE 服务器的高级配置。",
        "使用此向导配置 HPE 服务器上的网络接口。",
        "在执行任何更新之前，请仔细阅读固件发行说明。",
    ],
    'zh-tw': [
        "本指南說明了 HPE 伺服器的進階設定。",
        "請使用此精靈在 HPE 伺服器上設定網路介面。",
        "在執行任何更新之前，請仔細閱讀韌體版本資訊。",
    ],
    'ja': [
        "このガイドでは、HPE サーバーの高度な構成について説明します。",
        "このウィザードを使用して、HPE サーバー上のネットワーク インターフェイスを構成します。",
        "アップデートを適用する前に、ファームウェアのリリースノートを必ず確認してください。",
    ],
    'ko': [
        "이 가이드는 HPE 서버의 고급 구성에 대해 설명합니다.",
        "이 마법사를 사용하여 HPE 서버의 네트워크 인터페이스를 구성하십시오.",
        "업데이트를 적용하기 전에 펌웨어 릴리스 노트를 반드시 확인하십시오.",
    ],
}

print()
print("Samples by language code (for reference):")
for code, texts in all_lang_samples.items():
    for text in texts:
        print(f"- {code}: {repr(text)}")

snippets_all = [text for texts in all_lang_samples.values() for text in texts]

for friendly_name, code in codes_verify.items():
    print()
    print(f"Target language: {friendly_name} (code={code})")
    try:
        errs_prob_global = translation_errors_prob(snippets_all, [], [], friendly_name)
        print("Flag results per snippet:")
        for lc, texts in all_lang_samples.items():
            for text in texts:
                norm = postprocess(text)
                flagged = norm in errs_prob_global
                print("-", lc, "->", "FLAGGED" if flagged else "OK", "|", repr(text))
        print("Raw errors_prob:", errs_prob_global)
    except Exception as exc:
        print("Error while running translation_errors_prob for", friendly_name, ":", exc)