# Math Competition Hub — Production v1

一個可正式部署的數學競賽情報網站。

## 已包含
- Flask + PostgreSQL/SQLite
- Docker / docker-compose
- 公開競賽列表與篩選
- 年度資料模型：同一競賽可累積多年資料
- 歷屆試題資料表
- 來源與最後確認時間
- 變更紀錄模型
- 管理後台與手動更新
- Serper 網路搜尋整合
- GitHub Actions 每週自動更新
- Render 部署設定

## 本機測試
1. 複製 `.env.example` 成 `.env`
2. 修改 SECRET_KEY、ADMIN_EMAIL、ADMIN_PASSWORD
3. `docker compose up --build`
4. 開啟 http://localhost:8000
5. 管理後台：http://localhost:8000/admin

## 正式部署
### Render
1. 把此專案推到 GitHub。
2. 在 Render 建立 Web Service，使用 Docker。
3. 建立 PostgreSQL。
4. 設定環境變數：
   - DATABASE_URL
   - SECRET_KEY
   - ADMIN_EMAIL
   - ADMIN_PASSWORD
   - SERPER_API_KEY
5. 部署後測試 `/` 與 `/admin`。
6. GitHub Secrets 加入 DATABASE_URL、SECRET_KEY、SERPER_API_KEY、ADMIN_EMAIL、ADMIN_PASSWORD。
7. GitHub Actions 每週一 UTC 02:00 執行增量搜尋。

## 重要
搜尋器目前採「保守寫入」：搜尋結果會先與既有競賽比對，避免把搜尋摘要直接當成正式日期/費用。下一階段可增加官方頁面解析器與人工審核佇列，確認後才寫入報名日期、費用、試題。
