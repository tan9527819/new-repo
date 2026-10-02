# API-Football 足球数据分析

该仓库是一个用于足球赔率与比赛数据分析的起始模板，目标包括：

- 从 API-Football 拉取比赛与实时赔率数据；
- 建立 CSV 格式的历史赔率数据库；
- 实现相似盘型 / 历史同赔检索（基于赔率向量或特征相似度）；
- 赔率变盘（盘路）分析与可视化；
- 使用泊松分布进行进球率估计与校准（Poisson calibration）。

本仓库包含项目骨架、示例脚本与说明，便于后续开发与迭代。

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
   export API_FOOTBALL_BASE_URL="https://v3.football.api-sports.io"
   export HISTORICAL_DATA_PATH="./data/odds_history.csv"

5. 示例：读取历史 CSV 并列出最近比赛：

   python -c "from football_analysis.data import repository; print(repository.load_matches(10)[:3])"

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
  - api/                        API-Football 客户端与资源封装
  - data/                       数据拉取、清洗、存储模块
  - analysis/                   赔率/模型分析模块

当前已实现（第一阶段）

- API-Football 客户端基础实现（支持请求、超时、重试，读取 API_KEY 来自环境变量）
- 历史赔率 CSV Loader：自动识别常见列名、基础清洗并给出缺失提示（不修改原 CSV）
- 数据标准化：MatchRecord dataclass
- 历史数据接口（基于 pandas）：load_matches / find_similar_matches / find_same_odds / get_recent_results
- 单元测试骨架（pytest）

如何运行测试

- 在虚拟环境中安装依赖后运行：
  pytest -q

下一阶段建议

- 补全 API-Football 各资源的字段映射与分页
- 为历史 CSV 添加增量写入工具（append with dedupe）或迁移到 SQLite
- 实现更高级的相似度匹配（向量化、近似最近邻）
- 添加 CI（GitHub Actions）自动化测试

安全与注意事项

- API_KEY 仅来自环境变量，代码中不会包含真实密钥。
- .env 文件应加入 .gitignore，不要提交真实密钥。

