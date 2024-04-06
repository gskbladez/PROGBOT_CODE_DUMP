I_SCRIPT="import_script.sql"
DATA_TABLE="data_tables.sqlite3"
echo '.separator "\t" "\n"' > "$I_SCRIPT"

for f_name in ../*.tsv; do
    F_TABLE="${f_name%.tsv}"
    F_TABLE="${F_TABLE%data}"
    F_TABLE="${F_TABLE#../}"
    F_TABLE="${F_TABLE//[^a-zA-Z0-9_]/}"
    echo ".import $f_name $F_TABLE" >> "$I_SCRIPT"
done

rm -f "$DATA_TABLE"
sqlite3 $DATA_TABLE < "$I_SCRIPT"
sqlite3 $DATA_TABLE < "extra_fixes.sql"
rm -f "$I_SCRIPT"
