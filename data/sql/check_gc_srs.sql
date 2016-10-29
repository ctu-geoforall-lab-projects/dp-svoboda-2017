select  name
from    sqlite_master
where   type='table'
        and
        name in ('geometry_columns', 'spatial_ref_sys');
