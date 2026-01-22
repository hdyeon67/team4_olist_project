# Olist Seller Retention: Delay Threshold & Remaining Activity Loss

## [1] 프로젝트 개요 (Project Overview)

- **분석 상황 (Context)**:  
  Olist는 브라질 이커머스 마켓플레이스로, 셀러 생태계의 안정성은 플랫폼 지속성에 직결됩니다.  
  본 프로젝트는 배송 지연 경험이 셀러의 향후 활동 지속성에 미치는 영향을 셀러 관점에서 분석하고, 운영 개입이 필요한 임계 지연 기준을 도출합니다.

- **분석 목표 (Objectives)**:
  - 배송완료 주문이 충분한(≥50) 셀러를 대상으로 분석 표본을 안정화합니다.
  - 셀러의 **초기(첫 K건) 배송 지연 노출(exposure)** 을 정량화합니다.
  - 임계 지연일수(d)별로 **잔여 활동(remaining activity)의 손실(loss)** 을 비교하여 개입 기준을 제안합니다.

- **핵심 오디언스**:
  - 셀러 운영/품질 관리팀(SLA 정책)
  - 물류/배송 성능 모니터링 담당

## [2] 핵심 분석 결과 (Key Findings)
- 최종 결과 그래프: **Loss in remaining activity by delay threshold (first K orders)**
- (값 채우기) d가 증가함에 따라 노출군/비노출군의 잔여 활동 차이가 확대되는 구간을 임계 후보로 제안

---

## [3] 프로젝트 구조 및 설정 (Setup & Architecture)

### 📂 폴더 구조
- `data/`: 로컬 원본 데이터 저장 (Git 제외)
- `notebooks/`: 메인 분석 노트북
- `src/`: 전처리/노출/결과/임계 계산 모듈
- `reports/figures/`: 최종 결과 이미지 저장(선택)

### 🔧 환경 설정
Python 3.10+

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

- 첫 실행 시 노트북 상단 셀(환경 설정 + 폰트 설정)부터 순서대로 실행한 후,
  Kernel → Change Kernel → `team4-olist (.venv)` 선택을 권장합니다.



## [4] 협업 규칙 (Collaboration & Git Workflow)
- main 브랜치 보호: Pull Request 기반 merge
- 커밋 컨벤션:
   - [feat]: 기능 추가
   - [fix]: 버그 수정
   - [docs]: 문서 수정
   - [refactor]: 구조 개선

### ⚠️ 유의사항
- CSV 파일은 .gitignore에 의해 저장소에 업로드되지 않습니다.
- 로컬 data/ 폴더에 파일을 위치시키고 실행합니다.


---

# 12) 메인 노트북 `notebooks/main_seller_delay_threshold_loss.ipynb`

요청하신 대로 **로컬에서 바로 열 수 있는 ipynb(JSON) 형태**로 제공합니다.  
이 노트북은 “최종 그래프”만 만들도록 최소 구성입니다.

> 아래 내용을 그대로 `notebooks/main_seller_delay_threshold_loss.ipynb`로 저장하세요.

```json
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# Olist Seller Delay Threshold → Remaining Activity Loss\n",
        "\n",
        "목적: 최종 산출물 그래프\n",
        "- **Loss in remaining activity by delay threshold (first K orders)**\n",
        "\n",
        "원칙:\n",
        "- 그래프를 변경하지 않고, 필요한 로직만 모듈화하여 재현 가능하게 실행합니다.\n"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": null,
      "source": [
        "# =========================================\n",
        "# 0) Notebook 실행 준비: import path 설정\n",
        "# notebooks/ 폴더에서 실행하므로, 프로젝트 루트를 sys.path에 추가\n",
        "# =========================================\n",
        "import os, sys\n",
        "sys.path.append(os.path.abspath('..'))\n",
        "\n",
        "from src.config import CFG\n",
        "cfg = CFG()\n",
        "print('PROJECT_ROOT:', cfg.PROJECT_ROOT)\n",
        "print('DATA_DIR:', cfg.DATA_DIR)\n"
      ],
      "outputs": []
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": null,
      "source": [
        "# =========================================\n",
        "# 1) 데이터 로드\n",
        "# - orders + order_items 로드\n",
        "# =========================================\n",
        "from src.io import load_orders_items\n",
        "\n",
        "orders, items = load_orders_items(cfg)\n",
        "print('orders:', orders.shape)\n",
        "print('items:', items.shape)\n"
      ],
      "outputs": []
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": null,
      "source": [
        "# =========================================\n",
        "# 2) 주문-셀러 베이스(os) 생성\n",
        "# - delivered 필터\n",
        "# - delivery_delay_days, late_days 계산\n",
        "# =========================================\n",
        "from src.prep import build_order_seller_base, filter_sellers_by_min_orders\n",
        "\n",
        "os_df = build_order_seller_base(orders, items, cfg)\n",
        "print('os (before min seller orders filter):', os_df.shape)\n",
        "\n",
        "os_df = filter_sellers_by_min_orders(os_df, cfg)\n",
        "print('os (after min seller orders filter):', os_df.shape)\n"
      ],
      "outputs": []
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": null,
      "source": [
        "# =========================================\n",
        "# 3) 초기(첫 K건) 노출(exposure) 생성\n",
        "# - early_max_late, early_p95_late, early_severe7_rate\n",
        "# =========================================\n",
        "from src.exposure import build_early_exposure\n",
        "\n",
        "seller_early = build_early_exposure(os_df, cfg)\n",
        "print('seller_early:', seller_early.shape)\n",
        "seller_early.head()\n"
      ],
      "outputs": []
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": null,
      "source": [
        "# =========================================\n",
        "# 4) 잔여 활동(remaining activity) 계산\n",
        "# - 초기 K 이후 remaining_orders\n",
        "# =========================================\n",
        "from src.outcome import build_remaining_activity\n",
        "\n",
        "seller_outcome = build_remaining_activity(os_df, seller_early, cfg)\n",
        "print('seller_outcome:', seller_outcome.shape)\n",
        "seller_outcome.head()\n"
      ],
      "outputs": []
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": null,
      "source": [
        "# =========================================\n",
        "# 5) 임계 d별 remaining activity loss 계산\n",
        "# - 노출 정의: early_max_late >= d\n",
        "# - 결과: remaining_orders\n",
        "# =========================================\n",
        "from src.threshold import compute_loss_by_delay_threshold\n",
        "\n",
        "loss_df = compute_loss_by_delay_threshold(\n",
        "    seller_early=seller_early,\n",
        "    seller_outcome=seller_outcome,\n",
        "    cfg=cfg,\n",
        "    exposure_col='early_max_late',\n",
        "    outcome_col='remaining_orders'\n",
        ")\n",
        "\n",
        "loss_df.head(10)\n"
      ],
      "outputs": []
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": null,
      "source": [
        "# =========================================\n",
        "# 6) 최종 결과 그래프\n",
        "# - Loss in remaining activity by delay threshold (first K orders)\n",
        "# =========================================\n",
        "from src.viz import plot_loss_by_threshold\n",
        "\n",
        "plot_loss_by_threshold(loss_df, K=cfg.K_EARLY_ORDERS, exposure_col='early_max_late')\n"
      ],
      "outputs": []
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "name": "python",
      "version": "3.10"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
