"""数据库初始化脚本"""
import argparse
from sqlalchemy import text, DDL
from sqlalchemy.orm import Session

from app.db.base import engine, Base, SessionLocal
from app.db.models import DMaskSpec


def create_glasslayout_view() -> None:
    """创建glasslayout视图"""
    print("创建glasslayout视图...")
    
    # 根据数据库类型选择不同的视图创建方式
    from app.db.base import engine
    db_type = engine.url.drivername
    
    if db_type == 'oracle':
        # Oracle数据库视图创建
        view_sql = """CREATE OR REPLACE VIEW glasslayout AS
SELECT 
PANEL_NO as id,
PRODUCT_ID as tft_product,
PANEL_RIGHT_UP_X*1000 as x_right_up,
PANEL_RIGHT_UP_Y*1000 as y_right_up,
PANEL_RIGHT_DW_X*1000 as x_right_down,
PANEL_RIGHT_DW_Y*1000 as y_right_down,
PANEL_LEFT_UP_X*1000 as x_left_up,
PANEL_LEFT_UP_Y*1000 as y_left_up,
PANEL_LEFT_DW_X*1000 as x_left_down,
PANEL_LEFT_DW_Y*1000 as y_left_down
FROM PRODUCT_INFO@ADCDB P 
JOIN PRODUCT_LAYOUT@ADCDB L ON P.ID = L.PRODUCT_INFO_UID"""
        
        with engine.connect() as conn:
            conn.execute(text(view_sql))
            conn.commit()
        print("glasslayout视图创建完成")
    else:
        # 非Oracle数据库，不创建视图或使用替代方案
        print("  当前数据库类型不支持此视图创建，跳过视图创建")
        print("  视图创建完成（跳过）")


def add_fields_to_reasoncode() -> None:
    """为reasoncode表增加codetype和color字段"""
    print("为reasoncode表增加字段...")
    
    from app.db.base import engine
    db_type = engine.url.drivername
    
    # 检查reasoncode表是否存在
  
    with engine.connect() as conn:
        # 检查表是否存在
        table_exists = False
        if db_type == 'sqlite':
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='reasoncode'"))
            table_exists = result.fetchone() is not None
        elif db_type == 'oracle':
            # Oracle数据库检查表是否存在
            result = conn.execute(text("SELECT table_name FROM user_tables WHERE table_name = 'REASONCODE'"))
            table_exists = result.fetchone() is not None
        
        if not table_exists:
            print("  reasoncode表不存在，跳过字段添加")
            return
        
        # 根据数据库类型选择不同的字段检查和添加方式
        if db_type == 'sqlite':
            # SQLite数据库检查字段是否存在
            try:
                result = conn.execute(text("PRAGMA table_info(reasoncode)"))
                columns = result.fetchall()
                # 提取列名，统一转换为小写进行比较
                column_names = [row[1].lower() for row in columns]  # row[1]是字段名
                
                # 检查codetype字段
                if 'codetype' not in column_names:
                    conn.execute(text("ALTER TABLE reasoncode ADD codetype VARCHAR(20)"))
                    print("  已添加codetype字段")
                else:
                    print("  codetype字段已存在，跳过添加")
                
                # 检查color字段
                if 'color' not in column_names:
                    conn.execute(text("ALTER TABLE reasoncode ADD color VARCHAR(10)"))
                    print("  已添加color字段")
                else:
                    print("  color字段已存在，跳过添加")
            except Exception as e:
                print(f"  检查或添加字段时出错: {e}")
        elif db_type == 'oracle':
            # Oracle数据库检查字段是否存在
            try:
                check_fields_sql = """SELECT column_name 
                FROM user_tab_columns 
                WHERE table_name = 'REASONCODE' 
                AND column_name IN ('CODETYPE', 'COLOR')"""
                
                result = conn.execute(text(check_fields_sql))
                existing_fields = {row[0].upper() for row in result}
                
                # 添加codetype字段
                if 'CODETYPE' not in existing_fields:
                    conn.execute(text("ALTER TABLE reasoncode ADD (codetype VARCHAR2(20))"))
                    print("  已添加codetype字段")
                else:
                    print("  codetype字段已存在，跳过添加")
                
                # 添加color字段
                if 'COLOR' not in existing_fields:
                    conn.execute(text("ALTER TABLE reasoncode ADD (color VARCHAR2(10))"))
                    print("  已添加color字段")
                else:
                    print("  color字段已存在，跳过添加")
            except Exception as e:
                print(f"  检查或添加字段时出错: {e}")
        else:
            print(f"  不支持的数据库类型: {db_type}，跳过字段添加")
        
        conn.commit()
    print("reasoncode表字段添加完成")


def create_specific_tables(drop_existing: bool = False) -> None:
    """创建指定的表：MASK_SPEC和mac_defect_records"""
    print("创建指定表...")
    
    from app.db.base import engine
    db_type = engine.url.drivername
    
    if drop_existing:
        # 只删除指定的表
        print("  删除现有指定表...")
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS mac_defect_records CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS MASK_SPEC CASCADE"))
            conn.commit()
    
    # 根据数据库类型生成不同的SQL语句
    if db_type == 'sqlite':
        # SQLite数据库
        mask_spec_sql = """CREATE TABLE IF NOT EXISTS MASK_SPEC (
            PRODUCTSPECNAME VARCHAR(64),
            X_PANELS INTEGER,
            Y_PANELS INTEGER,
            FULL_SHOT INTEGER,
            REMARK VARCHAR(255),
            CREATEUSER VARCHAR(20),
            CREATETIME DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
        
        defect_records_sql = """CREATE TABLE IF NOT EXISTS mac_defect_records (
            UUID VARCHAR(64) NOT NULL,
            PROCESSOPERATIONNAME VARCHAR(20),
            PRODUCTNAME VARCHAR(64) NOT NULL,
            LOTNAME VARCHAR(20),
            PRODUCTREQUESTNAME VARCHAR(20),
            PRODUCTSPECNAME VARCHAR(20),
            DEFECT_CODE VARCHAR(20),
            DEFECT_TYPE VARCHAR(10),
            PANEL_ID TEXT,
            GEOM_DATA TEXT,
            PANEL_COUNT INTEGER,
            IS_SYMMETRY VARCHAR(1),
            REMARKS TEXT,
            MACHINENAME VARCHAR(20),
            OPERATOR_ID VARCHAR(20),
            INSPECTOR VARCHAR(100),
            CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (UUID)
        )"""
    else:
        # Oracle或其他数据库
        mask_spec_sql = """CREATE TABLE IF NOT EXISTS MASK_SPEC (
            PRODUCTSPECNAME VARCHAR2(64),
            X_PANELS INTEGER,
            Y_PANELS INTEGER,
            FULL_SHOT INTEGER,
            REMARK VARCHAR2(255),
            CREATEUSER VARCHAR2(20),
            CREATETIME TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
        )"""
        
        defect_records_sql = """CREATE TABLE IF NOT EXISTS mac_defect_records (
            UUID VARCHAR2(64) NOT NULL,
            PROCESSOPERATIONNAME VARCHAR2(20),
            PRODUCTNAME VARCHAR2(64) NOT NULL,
            LOTNAME VARCHAR2(20),
            PRODUCTREQUESTNAME VARCHAR2(20),
            PRODUCTSPECNAME VARCHAR2(20),
            DEFECT_CODE VARCHAR2(20),
            DEFECT_TYPE VARCHAR2(10),
            PANEL_ID CLOB,
            GEOM_DATA CLOB,
            PANEL_COUNT NUMBER(10),
            IS_SYMMETRY VARCHAR2(1),
            REMARKS CLOB,
            MACHINENAME VARCHAR2(20),
            OPERATOR_ID VARCHAR2(20),
            INSPECTOR VARCHAR2(100),
            CREATED_AT TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
            PRIMARY KEY (UUID)
        )"""
    
    # 创建MASK_SPEC表
    print("  创建MASK_SPEC表...")
    with engine.connect() as conn:
        conn.execute(text(mask_spec_sql))
    
    # 创建mac_defect_records表
    print("  创建mac_defect_records表...")
    with engine.connect() as conn:
        conn.execute(text(defect_records_sql))
        conn.commit()
    print("指定表创建完成")


def create_tables(drop_existing: bool = False) -> None:
    """创建所有数据库表（兼容原有接口）"""
    if drop_existing:
        print("删除现有表...")
        Base.metadata.drop_all(bind=engine)
    
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("表创建完成")


def init_db_based_on_file(drop_existing: bool = False) -> None:
    """基于spec/初始化.md的数据库初始化"""
    print("执行基于初始化.md的数据库初始化...")
    
    # 创建指定表
    create_specific_tables(drop_existing)
    
    # 为reasoncode表增加字段
    add_fields_to_reasoncode()
    
    # 创建glasslayout视图
    create_glasslayout_view()
    
    print("基于初始化.md的数据库初始化完成")


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="数据库初始化工具")
    parser.add_argument(
        "--full", 
        action="store_true", 
        help="执行完整初始化：创建表并插入数据（默认不删除现有表）"
    )
    parser.add_argument(
        "--create-tables", 
        action="store_true", 
        help="仅创建数据库表"
    )
    parser.add_argument(
        "--insert-data", 
        action="store_true", 
        help="仅插入初始测试数据"
    )
    parser.add_argument(
        "--drop-existing", 
        action="store_true", 
        help="在创建表前删除现有表（仅与--full或--create-tables配合使用）"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="基于spec/初始化.md执行数据库初始化：创建指定表、新增字段和视图，不插入数据"
    )
    
    return parser.parse_args()


def main() -> None:
    """主函数"""
    args = parse_arguments()
    
    try:
        if args.real:
            # 基于初始化.md的数据库初始化
            init_db_based_on_file(args.drop_existing)
        elif args.full:
            print("执行完整数据库初始化...")
            # 创建表
            create_tables(args.drop_existing)
        elif args.create_tables:
            create_tables(args.drop_existing)
        elif args.insert_data:
            print("已移除数据插入功能")
            print("基于初始化.md的初始化不支持插入数据")
        else:
            print("请指定要执行的操作：--real, --full 或 --create-tables")
            print("使用 --help 查看详细帮助")
            return
        
        print("数据库初始化操作完成！")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise


if __name__ == "__main__":
    main()