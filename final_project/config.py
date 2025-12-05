from typing import List, Dict, Any
import psycopg2

# Koneksi ke database PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5432",          # port default PostgreSQL
    user="postgres",      # ganti sesuai user PostgreSQL kamu
    password="0",  # ganti sesuai password PostgreSQL kamu
    dbname="multicultural_recipe"     # nama database
)

print("Koneksi PostgreSQL berhasil!")

# Membuat cursor
c = conn.cursor()

def _fetchall(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute a query and return results as a list of dicts."""
    if params is None:
        params = ()
    c.execute(query, params)
    rows = c.fetchall()
    columns = [desc[0] for desc in c.description] if c.description else []
    return [dict(zip(columns, row)) for row in rows]

# ============================
# Fungsi ambil data dari tabel
# ============================

def view_ingredient() -> List[Dict[str, Any]]:
    """List semua ingredient."""

    query = """
        SELECT ingredient_id, ingredient_name
        FROM ingredient_table
        ORDER BY ingredient_name ASC
    """
    return _fetchall(query)


def view_recipe_ingredient() -> List[Dict[str, Any]]:
    """List relasi resep-ingredient."""

    query = """
        SELECT
            ri.recipe_ingredient_id,
            r.recipe_name,
            i.ingredient_name
        FROM recipe_ingredient_table ri
        JOIN recipe_table r
          ON ri.recipe_id = r.recipe_id
        JOIN ingredient_table i
          ON ri.ingredient_id = i.ingredient_id
        ORDER BY ri.recipe_ingredient_id
    """
    c.execute(query)
    return c.fetchall()

def view_recipe():
    query = """
        SELECT
            r.recipe_id,
            r.recipe_name,
            tc.type_course_name,
            tcu.type_cuisine_name,
            td.type_diet_name
        FROM recipe_table r
        JOIN type_course_table  tc  ON r.type_course_id  = tc.type_course_id
        JOIN type_cuisine_table tcu ON r.type_cuisine_id = tcu.type_cuisine_id
        JOIN type_diet_name    td  ON r.type_diet_id     = td.type_diet_id
        ORDER BY r.recipe_name ASC
    """
    return _fetchall(query)


# ---------------------------------------------------------------------------
# Aggregation helpers for dashboards/visualizations
# ---------------------------------------------------------------------------

def recipe_count_by_cuisine() -> List[Dict[str, Any]]:
    """Jumlah resep per cuisine."""

    query = """
        SELECT
            tcu.type_cuisine_name AS cuisine,
            COUNT(*) AS recipe_count
        FROM recipe_table r
        JOIN type_cuisine_table tcu ON r.type_cuisine_id = tcu.type_cuisine_id
        GROUP BY tcu.type_cuisine_name
        ORDER BY recipe_count DESC, cuisine ASC
    """
    return _fetchall(query)


def recipe_category_count_by_cuisine() -> List[Dict[str, Any]]:
    """Jumlah kategori (type_course) dan resep per cuisine."""

    query = """
        SELECT
            tcu.type_cuisine_name AS cuisine,
            COUNT(DISTINCT tc.type_course_name) AS category_count,
            COUNT(*) AS recipe_count
        FROM recipe_table r
        JOIN type_cuisine_table tcu ON r.type_cuisine_id = tcu.type_cuisine_id
        JOIN type_course_table  tc  ON r.type_course_id = tc.type_course_id
        GROUP BY tcu.type_cuisine_name
        ORDER BY category_count DESC, cuisine ASC
    """
    return _fetchall(query)


def top_ingredients(limit: int = 10) -> List[Dict[str, Any]]:
    """Top-N ingredient yang paling sering dipakai."""

    query = """
        SELECT
            i.ingredient_name,
            COUNT(*) AS usage_count
        FROM recipe_ingredient_table ri
        JOIN ingredient_table i ON ri.ingredient_id = i.ingredient_id
        GROUP BY i.ingredient_name
        ORDER BY usage_count DESC, i.ingredient_name ASC
        LIMIT %s
    """
    return _fetchall(query, (limit,))


def ingredient_usage_distribution() -> List[Dict[str, Any]]:
    """Distribusi penggunaan ingredient di seluruh resep."""

    query = """
        SELECT
            i.ingredient_name,
            COUNT(*) AS total_usage,
            COUNT(DISTINCT ri.recipe_id) AS recipe_count
        FROM recipe_ingredient_table ri
        JOIN ingredient_table i ON ri.ingredient_id = i.ingredient_id
        GROUP BY i.ingredient_name
        ORDER BY total_usage DESC
    """
    return _fetchall(query)


def ingredient_count_per_recipe() -> List[Dict[str, Any]]:
    """Jumlah ingredient pada tiap resep."""

    query = """
        SELECT
            r.recipe_name,
            COUNT(ri.ingredient_id) AS ingredient_count
        FROM recipe_table r
        JOIN recipe_ingredient_table ri ON r.recipe_id = ri.recipe_id
        GROUP BY r.recipe_id, r.recipe_name
        ORDER BY ingredient_count DESC, r.recipe_name ASC
    """
    return _fetchall(query)


def ingredient_count_stats_by_cuisine() -> List[Dict[str, Any]]:
    """Statistik jumlah ingredient per resep untuk masing-masing cuisine."""

    query = """
        WITH per_recipe AS (
            SELECT
                tcu.type_cuisine_name AS cuisine,
                r.recipe_id,
                COUNT(ri.ingredient_id) AS ingredient_count
            FROM recipe_table r
            JOIN type_cuisine_table tcu ON r.type_cuisine_id = tcu.type_cuisine_id
            JOIN recipe_ingredient_table ri ON r.recipe_id = ri.recipe_id
            GROUP BY tcu.type_cuisine_name, r.recipe_id
        )
        SELECT
            cuisine,
            AVG(ingredient_count) AS avg_ingredient_per_recipe,
            MIN(ingredient_count) AS min_ingredient_per_recipe,
            MAX(ingredient_count) AS max_ingredient_per_recipe,
            COUNT(*) AS recipe_count
        FROM per_recipe
        GROUP BY cuisine
        ORDER BY avg_ingredient_per_recipe DESC, cuisine ASC
    """
    return _fetchall(query)


def recipe_count_by_diet() -> List[Dict[str, Any]]:
    """Jumlah resep per tipe diet."""

    query = """
        SELECT
            td.type_diet_name AS diet,
            COUNT(*) AS recipe_count
        FROM recipe_table r
        JOIN type_diet_name td ON r.type_diet_id = td.type_diet_id
        GROUP BY td.type_diet_name
        ORDER BY recipe_count DESC, diet ASC
    """
    return _fetchall(query)


def recipe_share_by_diet() -> List[Dict[str, Any]]:
    """Persentase pembagian resep per tipe diet."""

    query = """
        WITH counts AS (
            SELECT
                td.type_diet_name AS diet,
                COUNT(*) AS recipe_count
            FROM recipe_table r
            JOIN type_diet_name td ON r.type_diet_id = td.type_diet_id
            GROUP BY td.type_diet_name
        ), total AS (
            SELECT SUM(recipe_count) AS total_recipes FROM counts
        )
        SELECT
            counts.diet,
            counts.recipe_count,
            ROUND(counts.recipe_count::numeric / NULLIF(total.total_recipes, 0) * 100, 2) AS percentage_share
        FROM counts CROSS JOIN total
        ORDER BY counts.recipe_count DESC, counts.diet ASC
    """
    return _fetchall(query)


def ingredient_recipe_stats() -> List[Dict[str, Any]]:
    """Statistik jumlah resep dan penggunaan per ingredient."""

    query = """
        WITH total_recipe AS (
            SELECT COUNT(*) AS total FROM recipe_table
        ), ingredient_usage AS (
            SELECT
                i.ingredient_name,
                COUNT(DISTINCT ri.recipe_id) AS recipe_count,
                COUNT(*) AS total_usage
            FROM recipe_ingredient_table ri
            JOIN ingredient_table i ON ri.ingredient_id = i.ingredient_id
            GROUP BY i.ingredient_name
        )
        SELECT
            iu.ingredient_name,
            iu.recipe_count,
            iu.total_usage,
            ROUND(iu.recipe_count::numeric / NULLIF(tr.total, 0) * 100, 2) AS recipe_coverage_pct
        FROM ingredient_usage iu
        CROSS JOIN total_recipe tr
        ORDER BY iu.recipe_count DESC, iu.ingredient_name ASC
    """
    return _fetchall(query)


def recipe_overview_with_ingredient_count() -> List[Dict[str, Any]]:
    """Ringkasan resep beserta jumlah ingredient (berguna untuk tabel detail)."""

    query = """
        SELECT
            r.recipe_name,
            tc.type_course_name,
            tcu.type_cuisine_name,
            td.type_diet_name,
            COUNT(ri.ingredient_id) AS ingredient_count
        FROM recipe_table r
        JOIN recipe_ingredient_table ri ON r.recipe_id = ri.recipe_id
        JOIN type_course_table  tc  ON r.type_course_id  = tc.type_course_id
        JOIN type_cuisine_table tcu ON r.type_cuisine_id = tcu.type_cuisine_id
        JOIN type_diet_name    td  ON r.type_diet_id     = td.type_diet_id
        GROUP BY r.recipe_name, tc.type_course_name, tcu.type_cuisine_name, td.type_diet_name
        ORDER BY r.recipe_name ASC
    """
    return _fetchall(query)