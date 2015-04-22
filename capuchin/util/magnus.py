from capuchin import config
import psycopg2
import psycopg2.extras

def get_or_create_magnus_client(slug, name):
    connection = psycopg2.connect(
        database=config.SOURCE_DATABASE,
        port=config.SOURCE_PORT,
        user=config.SOURCE_USER,
        host=config.SOURCE_HOST,
        password=config.SOURCE_PASSWORD
    )
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("set schema 'magnus'")
    def fetch_client_id():
        cursor.execute("select client_id from clients where codename = %s", (slug,))
        rows = cursor.fetchall()
        if len(rows) == 1:
            return rows[0]['client_id']
        else:
            return None

    magnus_id = fetch_client_id()
    if not magnus_id:
        cursor.execute(
            "insert into clients (name, codename, created, updated) values (%s, %s, now(), now())",
            (name, slug)
        )
        magnus_id = fetch_client_id()
        connection.commit()

    return magnus_id
