SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE type IN ('table','index','trigger','view') ORDER BY type,name;
