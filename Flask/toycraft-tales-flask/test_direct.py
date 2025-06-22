import mysql.connector
from mysql.connector import Error

def test_direct_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Prianshu@123', 
              port=3306
        )
        
        if connection.is_connected():
            print("✅ Direct MySQL connection successful!")
            
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 MySQL Server version: {version[0]}")
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS toycraft_tales")
            cursor.execute("USE toycraft_tales")
            
            # Create table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45),
                    user_agent TEXT
                )
            """)
            
            # Test insert
            cursor.execute("""
                INSERT INTO contacts (name, email, phone, ip_address) 
                VALUES ('Test User', 'test@example.com', '1234567890', '127.0.0.1')
            """)
            connection.commit()
            
            # Test select
            cursor.execute("SELECT COUNT(*) FROM contacts")
            count = cursor.fetchone()[0]
            print(f"📝 Total contacts in database: {count}")
            
            cursor.close()
            connection.close()
            print("✅ Database setup completed successfully!")
            return True
            
    except Error as e:
        print(f"❌ Direct connection failed: {e}")
        
        if "Access denied" in str(e):
            print("\n💡 Password Solutions:")
            print("1. Check if your MySQL password is really 'Prianshu@123'")
            print("2. Try to connect manually:")
            print("   mysql -u root -p")
            print("3. Reset MySQL root password if needed:")
            print("   ALTER USER 'root'@'localhost' IDENTIFIED BY 'Prianshu@123';")
            
        elif "Can't connect" in str(e):
            print("\n💡 Service Solutions:")
            print("1. Start MySQL service:")
            print("   net start mysql (Windows)")
            print("2. Check MySQL status:")
            print("   mysqladmin -u root -p status")
            
        return False

if __name__ == "__main__":
    test_direct_connection()