# Shop App - MySQL Migration

Aplicatia a fost migrata de la SQLite la MySQL pentru performanta si scalabilitate mai buna.

## Informatii despre date

Toate informatiile sunt stocate in baza de date MySQL:

- **Produse**: Tabela `products` - toate produsele (shop + user)
- **Utilizatori**: Tabela `users` - conturile utilizatorilor
- **Administratori**: Tabela `admins` - conturile admin
- **Cos cumparaturi**: Tabela `cart` - produsele din cos (stocate ca JSON)
- **Produse cumparate**: Tabela `bought_products` - istoricul cumparaturilor
- **Comentarii**: Tabela `comments` - comentariile la produse
- **Rating-uri**: Tabela `ratings` - evaluarile produselor
- **Vizualizari**: Tabela `views` - numarul de vizualizari per produs
- **Favorite**: Tabela `favored` - produsele favorite ale utilizatorilor

## Setup MySQL

1. **Instaleaza MySQL**:
   - Pe Windows: Descarcă de pe https://dev.mysql.com/downloads/mysql/
   - Sau folosește XAMPP/WAMP care include MySQL

2. **Porneste MySQL service**:
   ```bash
   # Pe Windows cu MySQL instalat
   net start mysql

   # Sau cu XAMPP
   start xampp-control.exe si porneste MySQL
   ```

3. **Creeaza baza de date**:
   ```sql
   CREATE DATABASE shop_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'shop_user'@'localhost' IDENTIFIED BY 'parola_ta';
   GRANT ALL PRIVILEGES ON shop_db.* TO 'shop_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

4. **Seteaza variabilele de mediu** (optional):
   ```bash
   set DB_HOST=localhost
   set DB_USER=shop_user
   set DB_PASSWORD=parola_ta
   set DB_NAME=shop_db
   ```

   Sau editeaza `app.py` si modifica valorile default in sectiunea DATABASE SETUP.

5. **Ruleaza scriptul de setup**:
   ```bash
   python setup_mysql.py
   ```

## Probleme rezolvate

- ✅ **Adaugare la cos**: Frontend-ul trimitea obiectul produs complet, acum trimite formatul corect pentru CartItem
- ✅ **Adaugare comentarii**: Frontend-ul folosea `product.name`, acum foloseste `product.id`
- ✅ **Editare user**: Profilul user-ului este stocat in localStorage (browser), nu in baza de date
- ✅ **Adaugare produse**: Formularul functioneaza corect

## Rulare aplicatie

```bash
pip install -r requirements.txt
python app.py
```

Aplicatia va rula pe http://127.0.0.1:8000

## Backup/Restaurare date

Pentru a face backup al datelor din JSON files, ruleaza:

```bash
# Backup fisiere JSON
copy *.json backup\
```

Datele se vor migra automat din fisierele JSON in MySQL la primul run.