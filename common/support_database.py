
def get_att(att):
    if type(att) is str:
        return f'\'{att}\''
    else: return att

def _update_(table, fields, where):
    create_sql, condition = '',''
    for x in fields:
        create_sql += f'{x}=\'{fields[x]}\','
    for x in where:
        condition += f'{x}={get_att(where[x])} and'
    condition = condition[:-3]
    create_sql = create_sql[:-1]
    return f"Update {table} set {create_sql} where {condition}"


def _insert_(table, fields):
    _fields,values = '', ''
    for x in fields:
        _fields += f'{x},'
        values += f'{get_att(fields[x])},'
    _fields = _fields[0:-1]
    values = values[0:-1]
    return f'Insert into `{table}`({_fields}) values({values})'


# join co the la 1 table hoac dinh nghia 1 quan he
def find(join, fields, where):
    select, cond = '',''
    for x in fields:
        select += f'{x},'

    if where:
        for x in where:
            cond += f'{x}={getattr(where[x])} and'

    select = select[0:-1]
    cond = cond[0:-3]

    res = f'Select {select} from {join}'
    if cond != None:
        res += f'where {cond}'
    return res

