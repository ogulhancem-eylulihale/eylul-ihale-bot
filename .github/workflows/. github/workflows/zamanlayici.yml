name: Otomatik Ihale Tarayici

on:
  schedule:
    # Türkiye Saati ile 12:00 (UTC 09:00)
    - cron: '0 9 * * *'
    # Türkiye Saati ile 17:15 (UTC 14:15)
    - cron: '15 14 * * *'
  workflow_dispatch:

jobs:
  tara:
    runs-on: ubuntu-latest
    steps:
      - name: Kodlari Cek
        uses: actions/checkout@v3

      - name: Python Kur
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Taramayi Calistir
        run: python main.py
