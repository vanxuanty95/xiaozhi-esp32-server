# get_news_from_newsnow Plugin News Source Configuration Guide

## Overview

The `get_news_from_newsnow` plugin now supports dynamically configuring news sources through the Web management interface, no longer requiring code modifications. Users can configure different news sources for each agent in the Management Console.

## Configuration Methods

### 1. Configure Through Web Management Interface (Recommended)

1. Log in to the Management Console
2. Enter the "Role Configuration" page
3. Select the agent to configure
4. Click the "Edit Functions" button
5. Find the "newsnow News Aggregation" plugin in the right parameter configuration area
6. Enter semicolon-separated Chinese names in the "News Source Configuration" field

### 2. Configuration File Method

Configure in `config.yaml`:

```yaml
plugins:
  get_news_from_newsnow:
    url: "https://newsnow.busiyi.world/api/s?id="
    news_sources: "澎湃新闻;百度热搜;财联社;微博;抖音"
```

## News Source Configuration Format

News source configuration uses semicolon-separated Chinese names, format:

```
Chinese Name 1;Chinese Name 2;Chinese Name 3
```

### Configuration Example

```
澎湃新闻;百度热搜;财联社;微博;抖音;知乎;36氪
```

## Supported News Sources

The plugin supports the following news sources' Chinese names:

- 澎湃新闻
- 百度热搜
- 财联社
- 微博
- 抖音
- 知乎
- 36氪
- 华尔街见闻
- IT之家
- 今日头条
- 虎扑
- 哔哩哔哩
- 快手
- 雪球
- 格隆汇
- 法布财经
- 金十数据
- 牛客
- 少数派
- 稀土掘金
- 凤凰网
- 虫部落
- 联合早报
- 酷安
- 远景论坛
- 参考消息
- 卫星通讯社
- 百度贴吧
- 靠谱新闻
- And more...

## Default Configuration

If no news sources are configured, the plugin will use the following default configuration:

```
澎湃新闻;百度热搜;财联社
```

## Usage Instructions

1. **Configure News Sources**: Set news source Chinese names in the Web interface or configuration file, separated by semicolons
2. **Call Plugin**: Users can say "播报新闻" or "获取新闻"
3. **Specify News Source**: Users can say "播报澎湃新闻" or "获取百度热搜"
4. **Get Details**: Users can say "详细介绍这条新闻"

## How It Works

1. The plugin accepts Chinese names as parameters (e.g., "澎湃新闻")
2. Based on the configured news source list, converts Chinese names to corresponding English IDs (e.g., "thepaper")
3. Uses English IDs to call API to get news data
4. Returns news content to users

## Notes

1. Configured Chinese names must exactly match the names defined in CHANNEL_MAP
2. After configuration changes, the service needs to be restarted or configuration reloaded
3. If configured news sources are invalid, the plugin will automatically use default news sources
4. Multiple news sources are separated by English semicolons (;), do not use Chinese semicolons (；)
