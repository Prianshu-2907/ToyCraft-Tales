import mysql.connector
from mysql.connector import Error
from datetime import datetime

class Contact:
    """Contact object to make database results more consistent"""
    def __init__(self, data):
        if isinstance(data, dict):
            self.id = data.get('id')
            self.name = data.get('name')
            self.email = data.get('email')
            self.phone = data.get('phone')
            self.created_at = data.get('created_at')
            self.ip_address = data.get('ip_address')
            self.user_agent = data.get('user_agent')
        else:
            # Handle tuple/list data from cursor
            self.id = data[0] if len(data) > 0 else None
            self.name = data[1] if len(data) > 1 else None
            self.email = data[2] if len(data) > 2 else None
            self.phone = data[3] if len(data) > 3 else None
            self.created_at = data[4] if len(data) > 4 else None
            self.ip_address = data[5] if len(data) > 5 else None
            self.user_agent = data[6] if len(data) > 6 else None

class DatabaseManager:
    def __init__(self):
        # DIRECT CONNECTION - Replace with your actual credentials
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'Prianshu@123',  # Your actual password
            'database': 'toycraft_tales',
            'port': 3306
        }
        
        # Debug: Print configuration (without password)
        print(f"🔧 Database Config:")
        print(f"   Host: {self.config['host']}")
        print(f"   User: {self.config['user']}")
        print(f"   Database: {self.config['database']}")
        print(f"   Port: {self.config['port']}")
        print(f"   Password: {'***' if self.config['password'] else 'NOT SET'}")
        
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return None
    
    def init_database(self):
        """Initialize database and create tables"""
        connection = None
        cursor = None
        
        try:
            # First, connect without specifying database to create it
            temp_config = self.config.copy()
            temp_config.pop('database')
            
            print(f"🔗 Connecting to MySQL server...")
            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            print(f"✅ Database '{self.config['database']}' created/verified")
            
            cursor.execute(f"USE {self.config['database']}")
            
            # Create contacts table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            
            print("✅ Database and table created successfully!")
            
        except Error as e:
            print(f"❌ Error initializing database: {e}")
            
            # Provide specific help for common errors
            if "Access denied" in str(e):
                print("💡 Fix suggestions:")
                print("   1. Check your MySQL password")
                print("   2. Make sure MySQL service is running")
                print("   3. Try: mysql -u root -p")
                print("   4. If password is wrong, reset it")
                
            elif "Can't connect to MySQL server" in str(e):
                print("💡 Fix suggestions:")
                print("   1. Start MySQL service")
                print("   2. Check if MySQL is running on port 3306")
                
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def add_contact(self, name, email, phone, ip_address=None, user_agent=None):
        """Add a new contact to the database"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            if not connection:
                return False
                
            cursor = connection.cursor()
            
            insert_query = """
            INSERT INTO contacts (name, email, phone, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (name, email, phone, ip_address, user_agent))
            connection.commit()
            
            contact_id = cursor.lastrowid
            print(f"✅ Contact added successfully with ID: {contact_id}")
            return True
            
        except Error as e:
            print(f"❌ Error adding contact: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def get_all_contacts(self):
        """Get all contacts from database - returns Contact objects"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            if not connection:
                return []
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
            results = cursor.fetchall()
            
            # Convert dictionary results to Contact objects
            contacts = [Contact(row) for row in results]
            return contacts
            
        except Error as e:
            print(f"❌ Error fetching contacts: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def get_contact_count(self):
        """Get total number of contacts"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            if not connection:
                return 0
                
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            count = cursor.fetchone()[0]
            return count
            
        except Error as e:
            print(f"❌ Error getting contact count: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

# Initialize database manager
db_manager = DatabaseManager()