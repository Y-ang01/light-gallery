# 文件路径: scripts/simple_test.py
# 简单的数据库连接测试
import psycopg2
import sys


def simple_test():
    print("简单的数据库连接测试...")

    try:
        # 尝试连接
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="light-gallery",
            user="postgres",
            password="123456"
        )

        print("连接成功！")

        # 创建游标
        cur = conn.cursor()

        # 执行简单查询
        cur.execute("SELECT 1 + 1 as result")
        result = cur.fetchone()
        print(f"简单计算测试: 1 + 1 = {result[0]}")

        # 检查数据库
        cur.execute("SELECT current_database()")
        db_name = cur.fetchone()[0]
        print(f"当前数据库: {db_name}")

        # 清理
        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"连接失败: {e}")
        return False


if __name__ == "__main__":
    simple_test()