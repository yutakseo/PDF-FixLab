# PDF-FixLab
스캔한 PDF를 **바르게 만들기 위한 개인용 툴킷**입니다.

- 잘못 스캔된 페이지 **회전**
- 삐뚤어진 페이지를 **기울기 보정(deskew)**
- 여러 개로 나눠 스캔한 PDF **병합**
- 스캔 PDF에 **OCR 텍스트 레이어** 입혀서 검색 가능하게 만들기

를 한 번에 처리할 수 있게 만든 도구 모음입니다.



## 주요 기능

- `rotate-even`  
  짝수 페이지(2,4,6,...)만 180도 회전
- `rotate-all`  
  모든 페이지를 90/180/270도 회전
- `deskew`  
  각 페이지의 **미세한 기울기(±3° 정도)**만 자동 보정
- `ocr`  
  기존 PDF에 **OCR 텍스트 레이어 추가**  
  (Tesseract + ocrmypdf 사용, 텍스트 선택/검색 가능)
- `merge`  
  여러 PDF를 하나의 PDF로 병합



## 1. 설치

### 1-1. 로컬 파이썬 환경에서 설치

```bash
git clone https://github.com/<your-id>/pdfFixLab.git
cd pdfFixLab
pip install .
```

설치가 끝나면 어디서든 아래처럼 실행할 수 있습니다.

```bash
pdffixlab --help
```

개발하면서 수정 내용을 바로 바로 반영해서 쓰고 싶다면 editable 모드로 설치해도 됩니다.

```bash
pip install -e .
```


### 1-2. Docker로 사용(추천)

로컬에 Tesseract / Ghostscript / qpdf 설치하기 귀찮다면 Docker로 감싸서 쓸 수 있습니다.

```bash
git clone https://github.com/<your-id>/pdfFixLab.git
cd pdfFixLab
docker compose build
mkdir data
```

- 처리할 PDF 파일들을 `pdfFixLab/data/` 폴더에 넣어두면  
- 컨테이너 안에서는 `/data` 경로로 보입니다.

도움말 확인:

```bash
docker compose run --rm pdffixlab --help
```



## 2. 기본 사용법 (CLI)

기본 형식:

```bash
pdffixlab <command> [options...]
```

지원 명령어:

- `rotate-even` – 짝수 페이지 180° 회전
- `rotate-all` – 전체 페이지 회전
- `deskew` – 기울기 보정
- `ocr` – OCR 텍스트 레이어 추가
- `merge` – 여러 PDF 병합



### 2-1. 짝수 페이지 180도 회전: `rotate-even`

```bash
pdffixlab rotate-even <입력 PDF> <출력 PDF>
```

예시:

```bash
pdffixlab rotate-even part1_raw.pdf part1_rot.pdf
```

짝수 페이지(2,4,6,...)만 뒤집혀 스캔된 경우 한 번에 뒤집어 줄 때 사용합니다.



### 2-2. 전체 페이지 회전: `rotate-all`

```bash
pdffixlab rotate-all <입력 PDF> <출력 PDF> [--deg DEG]
```

- `--deg` : 시계 방향 회전 각도  
  (기본값: `270` → 오른쪽으로 90도 누워 있는 PDF를 왼쪽으로 90도 돌려서 바로 세움)

예시:

```bash
# 오른쪽으로 90도 누워있는 PDF를 바로 세우기
pdffixlab rotate-all part1_rot.pdf part1_upright.pdf --deg 270

# 상하 반전
pdffixlab rotate-all input.pdf flipped.pdf --deg 180
```



### 2-3. 기울기 보정: `deskew`

```bash
pdffixlab deskew <입력 PDF> <출력 PDF> [--dpi DPI]
```

- `--dpi` : PDF 페이지를 이미지로 렌더링할 때 사용할 DPI  
  (기본: 300, 스캔 교재는 300–600 사이 추천)

예시:

```bash
pdffixlab deskew part1_upright.pdf part1_deskew.pdf --dpi 600
```

내부적으로 OpenCV를 사용해 각 페이지의 텍스트 영역을 기준으로  
**작은 기울기(±3° 정도)**만 자동 보정합니다.  
90°씩 확 돌아가는 일은 없도록 각도 제한이 걸려 있습니다.



### 2-4. OCR 텍스트 레이어 추가: `ocr`

```bash
pdffixlab ocr <입력 PDF> <출력 PDF> [--lang LANG] [--deskew]
```

- `--lang` : Tesseract 언어 설정 (기본: `kor+eng`)
- `--deskew` : `ocrmypdf`의 내장 deskew 기능 사용 여부 (기본: 사용 안 함)

예시:

```bash
# 이미 회전/deskew를 해 둔 PDF에 텍스트 레이어만 입히기
pdffixlab ocr part1_deskew.pdf part1_ocr.pdf --lang kor+eng

# ocrmypdf의 내장 deskew까지 같이 쓰고 싶을 때
pdffixlab ocr input.pdf output_ocr.pdf --lang kor+eng --deskew
```

이렇게 만들어진 PDF는 겉으로는 스캔 이미지 그대로지만,  
텍스트 선택/복사 및 `Ctrl+F` 검색이 가능해집니다.

> ⚠️ 로컬에서 `ocr` 기능을 사용하려면:
>
> - `tesseract`
> - `gswin64c` (Ghostscript)
> - `qpdf`  
>
> 가 OS에 설치되어 있고,  
> `tesseract --version`, `gswin64c -version`, `qpdf --version` 이 정상 동작해야 합니다.  
> Docker 이미지는 이 의존성들을 기본 포함하도록 구성하는 것을 권장합니다.



### 2-5. 여러 PDF 병합: `merge`

```bash
pdffixlab merge <출력 PDF> <입력1> <입력2> ...
```

예시:

```bash
pdffixlab merge book_merged.pdf part1_ocr.pdf part2_ocr.pdf part3_ocr.pdf
```

인자로 넘긴 순서대로 페이지가 이어집니다.  
분권 스캔한 교재를 보정/OCR 후 한 권으로 합칠 때 유용합니다.



## 3. 예시 워크플로 (스캔 교재 한 권 처리)

**상황**  
한 권의 책을 세 부분으로 나눠서 스캔했고, 짝수 페이지는 뒤집혀 있고,  
전체적으로 약간씩 기울어져 있는 상태:

- `part1_raw.pdf`
- `part2_raw.pdf`
- `part3_raw.pdf`



### 3-1. 짝수 페이지 180도 회전

```bash
pdffixlab rotate-even part1_raw.pdf part1_rot.pdf
pdffixlab rotate-even part2_raw.pdf part2_rot.pdf
pdffixlab rotate-even part3_raw.pdf part3_rot.pdf
```



### 3-2. 전체 방향 바로 세우기 (필요한 경우)

```bash
pdffixlab rotate-all part1_rot.pdf part1_upright.pdf --deg 270
pdffixlab rotate-all part2_rot.pdf part2_upright.pdf --deg 270
pdffixlab rotate-all part3_rot.pdf part3_upright.pdf --deg 270
```



### 3-3. 기울기 보정

```bash
pdffixlab deskew part1_upright.pdf part1_deskew.pdf --dpi 600
pdffixlab deskew part2_upright.pdf part2_deskew.pdf --dpi 600
pdffixlab deskew part3_upright.pdf part3_deskew.pdf --dpi 600
```



### 3-4. OCR 텍스트 레이어 추가

```bash
pdffixlab ocr part1_deskew.pdf part1_ocr.pdf --lang kor+eng
pdffixlab ocr part2_deskew.pdf part2_ocr.pdf --lang kor+eng
pdffixlab ocr part3_deskew.pdf part3_ocr.pdf --lang kor+eng
```



### 3-5. 한 권으로 병합

```bash
pdffixlab merge book_merged.pdf part1_ocr.pdf part2_ocr.pdf part3_ocr.pdf
```

이렇게 하면 `book_merged.pdf` 하나로:

- 페이지 방향/기울기 정리되어 있고
- 텍스트 선택/복사/검색까지 되는

**최종본 PDF**를 얻을 수 있습니다.



## 4. Docker로 같은 작업 하기
`pdfFixLab` 루트 기준:

```bash
# 이미지 빌드
docker compose build

# data 폴더에 원본 PDF 넣기
cp ~/somewhere/part1_raw.pdf data/
cp ~/somewhere/part2_raw.pdf data/
cp ~/somewhere/part3_raw.pdf data/
```

이후 예를 들어:

```bash
docker compose run --rm pdffixlab deskew part1_raw.pdf part1_deskew.pdf --dpi 600
docker compose run --rm pdffixlab ocr part1_deskew.pdf part1_ocr.pdf --lang kor+eng
docker compose run --rm pdffixlab merge book_merged.pdf part1_ocr.pdf part2_ocr.pdf part3_ocr.pdf
```

- 컨테이너의 작업 디렉토리는 `/data`
- 호스트의 `./data` 와 볼륨으로 연결되어 있습니다.



## 5. 프로젝트 구조

개발용 프로젝트 구조는 다음과 같습니다.

```text
pdfFixLab/
├─ pdf_fix_lab/
│  ├─ __init__.py
│  ├─ rotate.py      # 회전 기능 (짝수 페이지 180도, 전체 회전 등)
│  ├─ deskew.py      # 기울기 보정
│  ├─ ocr_layer.py   # OCR 텍스트 레이어 추가 (ocrmypdf 래핑)
│  ├─ merge.py       # 여러 PDF 병합
│  └─ cli.py         # CLI 엔트리포인트 (pdffixlab)
├─ pyproject.toml    # 패키지 메타데이터/의존성/스크립트 엔트리 정의
├─ README.md
├─ Dockerfile
└─ docker-compose.yml
```

로컬 개발 시:

```bash
cd pdfFixLab
pip install -e .
pdffixlab --help
```



## 6. TODO / 아이디어

- `pipeline` 서브커맨드 추가  
  (`rotate-even → rotate-all → deskew → ocr → merge` 를 한 번에 실행)
- 특정 페이지 범위만 처리하는 옵션 (`--pages 5-20` 등)
- 간단한 웹 UI or GUI 추가
- PyPI 배포 (`pip install pdfFixLab`) 지원



## 라이선스

개인용 / 연구용으로 사용 중입니다.  
공개 라이선스는 추후 결정 예정입니다.
