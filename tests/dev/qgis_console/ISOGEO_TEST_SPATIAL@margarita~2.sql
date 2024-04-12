select "classe".owner, "classe".table_name, "colonne".column_name from
(select
    sys.all_tables.owner, sys.all_tables.table_name
    from sys.USER_TABLES
    join sys.ALL_TABLES
        on sys.user_tables.table_name = sys.all_tables.table_name
    where
        sys.all_tables.secondary = 'N' and
        sys.all_tables.owner not in ('GSMADMIN_INTERNAL', 'ORDDATA', 'SDE', 'ANONYMOUS','CTXSYS','DBSNMP','EXFSYS','LBACSYS','MDSYS','MGMT_VIEW','OLAPSYS','OWBSYS','ORDPLUGINS','ORDSYS','SI_INFORMTN_SCHEMA','SYS','SYSMAN','SYSTEM','TSMSYS','WK_TEST','WKPROXY','WMSYS','XDB','APEX_040000','APEX_PUBLIC_USER','DIP','FLOWS_30000','FLOWS_FILES','MDDATA','ORACLE_OCM','XS$NULL','SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR','PUBLIC','OUTLN','WKSYS','APEX_040200')
union
select
    v.OWNER, v.VIEW_NAME
    from sys.all_views v
    where 
        v.owner not in ('GSMADMIN_INTERNAL', 'ORDDATA', 'SDE', 'ANONYMOUS','CTXSYS','DBSNMP','EXFSYS','LBACSYS','MDSYS','MGMT_VIEW','OLAPSYS','OWBSYS','ORDPLUGINS','ORDSYS','SI_INFORMTN_SCHEMA','SYS','SYSMAN','SYSTEM','TSMSYS','WK_TEST','WKPROXY','WMSYS','XDB','APEX_040000','APEX_PUBLIC_USER','DIP','FLOWS_30000','FLOWS_FILES','MDDATA','ORACLE_OCM','XS$NULL','SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR','PUBLIC','OUTLN','WKSYS','APEX_040200')
) "classe"
left join (
select
    sys.all_tables.owner, sys.all_tables.table_name, col.column_name
    from sys.USER_TABLES
    join sys.ALL_TABLES
        on sys.user_tables.table_name = sys.all_tables.table_name
    left join sys.all_tab_cols col
        on sys.all_tables.OWNER = col.owner and sys.all_tables.table_name = col.table_name
    where
        sys.all_tables.secondary = 'N' and
        col.data_type = 'SDO_GEOMETRY' and 
        sys.all_tables.owner not in ('GSMADMIN_INTERNAL', 'ORDDATA', 'SDE', 'ANONYMOUS','CTXSYS','DBSNMP','EXFSYS','LBACSYS','MDSYS','MGMT_VIEW','OLAPSYS','OWBSYS','ORDPLUGINS','ORDSYS','SI_INFORMTN_SCHEMA','SYS','SYSMAN','SYSTEM','TSMSYS','WK_TEST','WKPROXY','WMSYS','XDB','APEX_040000','APEX_PUBLIC_USER','DIP','FLOWS_30000','FLOWS_FILES','MDDATA','ORACLE_OCM','XS$NULL','SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR','PUBLIC','OUTLN','WKSYS','APEX_040200')
union
select
    v.OWNER, v.VIEW_NAME, col.column_name
    from sys.all_views v
    left join sys.all_tab_cols col
        on v.OWNER = col.owner and v.VIEW_NAME = col.table_name
    where 
        col.data_type = 'SDO_GEOMETRY' and 
        v.owner not in ('GSMADMIN_INTERNAL', 'ORDDATA', 'SDE', 'ANONYMOUS','CTXSYS','DBSNMP','EXFSYS','LBACSYS','MDSYS','MGMT_VIEW','OLAPSYS','OWBSYS','ORDPLUGINS','ORDSYS','SI_INFORMTN_SCHEMA','SYS','SYSMAN','SYSTEM','TSMSYS','WK_TEST','WKPROXY','WMSYS','XDB','APEX_040000','APEX_PUBLIC_USER','DIP','FLOWS_30000','FLOWS_FILES','MDDATA','ORACLE_OCM','XS$NULL','SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR','PUBLIC','OUTLN','WKSYS','APEX_040200')
) "colonne"
on "classe".owner = "colonne".owner and "classe".table_name = "colonne".table_name