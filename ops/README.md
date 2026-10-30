# 每日资讯的独立触发

GitHub 的 schedule 可能延迟甚至丢弃，不能作为准点晨报的唯一时钟。这里的程序由现有 ECS 的 systemd timer 短暂调用，只检查公开网站并请求 GitHub 工作流；RSS、模型、API 密钥、MD 和构建仍在 GitHub，不向 ECS 复制新闻归档。

`fazhi-news-trigger.timer` 计划在北京时间 07:20、07:45、08:15、08:45、09:15、13:15、16:15 检查。当天页面及内容版本已一致则退出；有运行中的工作流则等待；成功发起补跑后有 20 分钟冷却。原 GitHub 定时作为另一路备份保留。两路仍依赖 GitHub 执行器和模型 API，不保证任何外部平台故障期间准点成功。

服务为 oneshot，使用独立无登录用户；内存上限 48 MB、CPU 配额 10%、最长 75 秒。timer 设 `Persistent=true` 并随系统启动。实测仅公开检查约 0.8 秒、20 MB 内存，退出后无常驻进程。

## 最小权限

推荐专用私有 GitHub App，仅安装到 `Gordoncee/morning-briefing-site`，只授予 Actions 读写和自动附带的 Metadata 只读。不授予 Contents、Secrets 或个人账号权限。每次需要补跑时短暂生成安装令牌，并再次限制为这一个仓库与 Actions 写；令牌不落盘。App 密钥仅放 `/etc/fazhi-news-trigger/app-key.pem`，服务用户所有、权限 0600；不复制本机 GitHub CLI 的登录凭证。

`register_github_app.py` 是本机一次性辅助授权页：仅监听回环地址，校验随机 state，由所有者在 GitHub 确认创建、选择唯一资讯仓库并安装。它从 GitHub API 安全取得生成的专用密钥，不显示密钥，丢弃不用的客户端与 webhook 密钥。完成 SSH 安装后应停止辅助页并删除本机临时密钥。

`/etc/fazhi-news-trigger/app.json` 只含配置：

```json
{
  "repository": "Gordoncee/morning-briefing-site",
  "client_id": "从 GitHub 取得的专用 App Client ID",
  "installation_id": 0,
  "private_key_file": "/etc/fazhi-news-trigger/app-key.pem"
}
```

先安装脚本和 unit、验证 unit，再完成专用应用的唯一仓库授权与密钥安装。实际实测补跑、确认 GitHub 成功及官网内容一致后，才启用 timer；不能把缺少凭证的已安装配置视为生效。

## 运维

```sh
# 只读检查，不读取凭证、不触发工作流
python3 /opt/fazhi-news-trigger/check_daily_news.py --dry-run

# 完成授权后，启用并查看持久状态
systemctl enable --now fazhi-news-trigger.timer
systemctl list-timers fazhi-news-trigger.timer
systemctl status fazhi-news-trigger.service
journalctl -u fazhi-news-trigger.service -n 20 --no-pager

# 停用独立触发，不影响 GitHub 自身定时或网站
systemctl disable --now fazhi-news-trigger.timer
```

工作记录只保存最后一次补跑的日期和时间戳，不存文章或模型数据。日志只输出公开日期、原因、运行编号等，不记录令牌、请求头或 API 响应正文。密钥泄露时应在 GitHub App 设置撤销该专用私钥并更新服务器；停用时撤销 App 安装。
