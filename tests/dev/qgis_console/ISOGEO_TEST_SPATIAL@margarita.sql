select
    col.owner as owner_name, col.table_name as table_name, col.column_name as geo_column, md.srid as geo_srid
    from sys.all_tab_cols col
    left join user_sdo_geom_metadata md
        on col.table_name = md.table_name
    where
        col.data_type = 'SDO_GEOMETRY'
        and col.owner not in ('GSMADMIN_INTERNAL', 'ORDDATA', 'SDE', 'ANONYMOUS','CTXSYS','DBSNMP','EXFSYS','LBACSYS','MDSYS','MGMT_VIEW','OLAPSYS','OWBSYS','ORDPLUGINS','ORDSYS','SI_INFORMTN_SCHEMA','SYS','SYSMAN','SYSTEM','TSMSYS','WK_TEST','WKPROXY','WMSYS','XDB','APEX_040000','APEX_PUBLIC_USER','DIP','FLOWS_30000','FLOWS_FILES','MDDATA','ORACLE_OCM','XS$NULL','SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR','PUBLIC','OUTLN','WKSYS','APEX_040200')
    order by col.table_name