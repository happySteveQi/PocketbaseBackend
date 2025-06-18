FROM --platform=linux/amd64 alpine:3.18

# 安装基础依赖（比如 for SSL）
RUN apk add --no-cache ca-certificates tzdata

# 创建目录结构
WORKDIR /app
COPY pocketbase /app/pocketbase
#COPY pb_migrations /app/pb_migrations

# 挂载数据目录
VOLUME ["/app/pb_data"]
EXPOSE 8090

# 启动 PocketBase
CMD ["./pocketbase", "serve", "--http=0.0.0.0:8090"] 