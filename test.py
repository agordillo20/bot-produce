import imputacion_v2

cookie = "EB217E3BB2950AC3E811EB40B6663CC4"
oid = "352935"

imp = imputacion_v2.imputacion()
imp.user_id = oid
imp.cookies['JSESSIONID'] = cookie
res = imp.get_actual_data()
print(res)