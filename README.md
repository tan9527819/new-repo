# API-Football 足球数据分析

该仓库是一个用于足球赔率与比赛数据分析的起始模板，目标包括：

- 从 API-Football 拉取比赛与实时赔率数据；
- 建立 CSV 格式的历史赔率数据库；
- 实现相似盘型 / 历史同赔检索（基于赔率向量或特征相似度）；
- 赔率变盘（盘路）分析与可视化；
- 使用泊松分布进行进球率估计与校准（Poisson calibration）。

本仓库仅包含项目骨架、示例脚本与说明，便于后续开发与迭代。

快速开始

1. 克隆仓库：

   git clone https://github.com/tan9527819/new-repo.git
   cd new-repo

2. 准备 Python 环境（推荐 Python 3.10+）：

   python -m venv .venv
   source .venv/bin/activate  # macOS / Linux
   # .venv\Scripts\activate  # Windows

3. 安装依赖：

   pip install -r requirements.txt

4. 配置环境变量（参考 .env.example）：

   export API_FOOTBALL_KEY="your_api_football_key"
   export ODDS_DB_PATH="./data/odds_history.csv"

5. 示例：拉取数据并保存为 CSV（后续需要完善）：

   python -m football_analysis.data.ingest

项目结构说明

- README.md                     本文件
- .gitignore
- requirements.txt              Python 依赖清单
- .env.example                  环境变量示例
- data/                         存放 CSV/数据库文件（不要提交大型数据到仓库）
  - README.md
- notebooks/                    实验与可视化 notebook
  - README.md
- src/football_analysis/        Python 包源码（主开发目录）
  - data/                       数据拉取、清洗、存储模块
    - ingest.py                 拉取 API-Football 与保存到 CSV 的示例脚本
  - analysis/                   赔率/模型分析模块
    - odds_analysis.py         赔率变盘与相似盘型分析的占位文件
    - poisson.py               泊松模型与校准的占位文件

开发与贡献

- 建议在 feature 分支上开发并通过 Pull Request 合并到 main。
- 将 API 密钥放在本地环境变量或 .env（不要把实际密钥提交到仓库）。

下一步建议

- 将 API-Football 的数据拉取逻辑补全并做重试/限流处理；
- 设计 CSV 的列与索引格式并实现增量更新；
- 实现相似盘型检索的向量化方法（如基于赔率比、对数差值或 embedding）；
- 增加测试目录与 CI（例如 GitHub Actions）用于自动化测试与 lint。

