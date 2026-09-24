import os
import secrets
from flask import Blueprint, request, Response, render_template, redirect, url_for
from functools import wraps
from datetime import datetime
from redis_db import conexion_redis

admin_bp = Blueprint('admin', __name__)

def requiere_auth(f):
    # Devolvemos la función decorada pero 
    # Con los metadatos de la original para que python lo diferencie
    @wraps(f)
    def decorada(*args, **kwargs):
        auth = request.authorization
        user_env = os.environ.get("ADMIN_USER", "")
        pass_env = os.environ.get("ADMIN_PASS", "")
        
        # Usamos secrets.compare_digest para evitar Timing Attacks (CWE-208)
        if not auth or not (secrets.compare_digest(auth.username, user_env) and secrets.compare_digest(auth.password, pass_env)):
            # Usamos Basic Auth para autenticar el administrador 
            return Response(
                'Acceso denegado. Introduce credenciales.', 401,
                {'WWW-Authenticate': 'Basic realm="Login de Administrador"'}
            )
        return f(*args, **kwargs)
    return decorada

# ESTADÍSTICAS
@admin_bp.route(f"/{os.environ.get('ADMIN_PATH', 'admin-default')}")
@requiere_auth
def admin_stats():
    # Usamos scan para no bloquear el Event Loop de Redis
    claves_stats = list(conexion_redis.scan_iter(match="stats:*"))
    todas_las_stats = {}
    embudos_facultades = {}
    for clave in claves_stats:
        nombre_facultad = clave.decode('utf-8').replace("stats:", "")
        datos_raw = conexion_redis.hgetall(clave)
        datos_limpios = {k.decode('utf-8'): int(v.decode('utf-8')) for k, v in datos_raw.items()}
        todas_las_stats[nombre_facultad] = datos_limpios
        
        # Extraemos el embudo específico de esta facultad
        datos_emb_fac_raw = conexion_redis.hgetall(f"embudo_facultad:{nombre_facultad}")
        embudo_fac = {k.decode('utf-8'): int(v.decode('utf-8')) for k, v in datos_emb_fac_raw.items()}
        total_fac = embudo_fac.get('1_qr', 0)
        embudos_facultades[nombre_facultad] = {}
        for fase in ['1_qr', '2_email', '3_password']:
            cantidad = embudo_fac.get(fase, 0)
            porcentaje = (cantidad / total_fac * 100) if total_fac > 0 else 0
            embudos_facultades[nombre_facultad][fase] = {"cantidad": cantidad, "porcentaje": round(porcentaje, 2)}
            
    # Manejamos las estadísticas del embudo
    # mostraremos a qué fase del engaño hemos llegado
    datos_embudo_raw = conexion_redis.hgetall("embudo:fase")
    embudo = {k.decode('utf-8'): int(v.decode('utf-8')) for k, v in datos_embudo_raw.items()}
    
    # Calculamos los porcentajes de conversión del embudo 
    # (tomando 1_qr como el 100%)
    total_escaneos = embudo.get('1_qr', 0)
    estadisticas_embudo = {}
    
    for fase in ['1_qr', '2_email', '3_password']:
        cantidad = embudo.get(fase, 0)
        porcentaje = (cantidad / total_escaneos * 100) if total_escaneos > 0 else 0
        estadisticas_embudo[fase] = {
            "cantidad": cantidad,
            "porcentaje": round(porcentaje, 2)
        }
    
    # Métricas temporales rápidas (Impactos contabilizados desde esta misma madrugada)
    hoy_inicio = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    impactos_hoy = conexion_redis.zcount("timeline:global:3_password", hoy_inicio, "+inf")

    # Distribución por horas de la afluencia
    elementos_qr = conexion_redis.zrange("timeline:global:1_qr", 0, -1, withscores=True)
    distribucion_horas = {str(i).zfill(2): 0 for i in range(24)} # Inicializar 00 a 23 en 0
    for miembro, score in elementos_qr:
        hora = datetime.fromtimestamp(score).strftime("%H")
        distribucion_horas[hora] += 1

    # MÉTRICAS DE CUARENTENA (integridad del dato)
    # "Impactos limpios" son los que sí cuentan (dedup por email). Los
    # "apartados" son envíos marcados como sospechosos que NO contaminan la
    # estadística pero quedan grabados para el análisis forense de la memoria.
    total_limpios = int(conexion_redis.get("cuarentena:total_limpios") or 0)
    total_sospechosos = int(conexion_redis.get("cuarentena:total_sospechosos") or 0)
    total_eventos = total_limpios + total_sospechosos
    senales_raw = conexion_redis.hgetall("cuarentena:senales")
    desglose_senales = {k.decode('utf-8'): int(v.decode('utf-8')) for k, v in senales_raw.items()}
    cuarentena = {
        "total_eventos": total_eventos,
        "limpios": total_limpios,
        "sospechosos": total_sospechosos,
        "senales": desglose_senales,
    }

    return render_template(
        'admin.html',
        stats=todas_las_stats,
        embudo=estadisticas_embudo,
        embudos_facultades=embudos_facultades,
        impactos_hoy=impactos_hoy,
        distribucion_horas=distribucion_horas,
        cuarentena=cuarentena,
    )

# PANEL DE EXPORTACIÓN CSV
@admin_bp.route(f"/{os.environ.get('ADMIN_PATH', 'admin-default')}/csv")
@requiere_auth
def admin_stats_csv():
    claves_stats = list(conexion_redis.scan_iter(match="stats:*"))
    def generar_csv():
        # EMBUDO GLOBAL
        yield "--- EMBUDO DE CONVERSION GLOBAL ---\n"
        yield "Fase,Cantidad,Porcentaje\n"
        
        datos_embudo_raw = conexion_redis.hgetall("embudo:fase")
        embudo = {k.decode('utf-8'): int(v.decode('utf-8')) for k, v in datos_embudo_raw.items()}
        total_global = embudo.get('1_qr', 0)
        
        for fase in ['1_qr', '2_email', '3_password']:
            cantidad = embudo.get(fase, 0)
            porcentaje = round((cantidad / total_global * 100), 2) if total_global > 0 else 0
            yield f'"{fase}",{cantidad},{porcentaje}%\n'
            
        yield "\n"
        
        # EMBUDOS POR FACULTAD
        yield "--- EMBUDOS POR FACULTAD ---\n"
        yield "Facultad,Fase,Cantidad,Porcentaje\n"
        yield "--- EMBUDOS POR ZONA/CENTRO ---\n"
        yield "Zona,Fase,Cantidad,Porcentaje\n"
        for clave in claves_stats:
            nombre_facultad = clave.decode('utf-8').replace("stats:", "")
            datos_emb_fac_raw = conexion_redis.hgetall(f"embudo_facultad:{nombre_facultad}")
            embudo_fac = {k.decode('utf-8'): int(v.decode('utf-8')) for k, v in datos_emb_fac_raw.items()}
            total_fac = embudo_fac.get('1_qr', 0)
            
            for fase in ['1_qr', '2_email', '3_password']:
                cantidad = embudo_fac.get(fase, 0)
                porcentaje = round((cantidad / total_fac * 100), 2) if total_fac > 0 else 0
                yield f'"{nombre_facultad}","{fase}",{cantidad},{porcentaje}%\n'
                
        yield "\n"
        
        # IMPACTOS POR UBICACION
        yield "--- IMPACTOS POR UBICACION ---\n"
        yield "Facultad,Ubicacion,Impactos\n"
        yield "--- IMPACTOS POR UBICACIÓN ---\n"
        yield "Zona,Ubicacion,Impactos\n"
        for clave in claves_stats:
            nombre_facultad = clave.decode('utf-8').replace("stats:", "")
            datos_raw = conexion_redis.hgetall(clave)
            for k, v in datos_raw.items():
                # Uso yield para no saturar la RAM del servidor
                yield f'"{nombre_facultad}","{k.decode("utf-8")}",{int(v.decode("utf-8"))}\n'
        
        yield "\n"
        
        # SERIE TEMPORAL GLOBAL (FASES)
        yield "--- SERIE TEMPORAL GLOBAL (POR FASES) ---\n"
        yield "Fase,VisitorID,Fecha,Hora,Timestamp\n"
        for fase in ['1_qr', '2_email', '3_password']:
            elementos = conexion_redis.zrange(f"timeline:global:{fase}", 0, -1, withscores=True)
            for miembro, score in elementos:
                dt = datetime.fromtimestamp(score)
                yield f'"{fase}","{miembro.decode("utf-8")}","{dt.strftime("%Y-%m-%d")}","{dt.strftime("%H:%M:%S")}",{int(score)}\n'
                
        yield "\n"
        
        # SERIE TEMPORAL POR UBICACIONES
        yield "--- SERIE TEMPORAL DE IMPACTOS POR UBICACION ---\n"
        yield "Centro,Ubicacion,EmailHash,Fecha,Hora,Timestamp\n"
        claves_timeline_ub = list(conexion_redis.scan_iter(match="timeline_ubicacion:*"))
        for clave in claves_timeline_ub:
            partes = clave.decode('utf-8').split(':')
            if len(partes) == 3:
                centro, ubicacion = partes[1], partes[2]
                elementos = conexion_redis.zrange(clave, 0, -1, withscores=True)
                for miembro, score in elementos:
                    dt = datetime.fromtimestamp(score)
                    yield f'"{centro}","{ubicacion}","{miembro.decode("utf-8")}","{dt.strftime("%Y-%m-%d")}","{dt.strftime("%H:%M:%S")}",{int(score)}\n'

        yield "\n"

        # RESUMEN DE CUARENTENA (integridad del dato)
        total_limpios = int(conexion_redis.get("cuarentena:total_limpios") or 0)
        total_sospechosos = int(conexion_redis.get("cuarentena:total_sospechosos") or 0)
        yield "--- RESUMEN DE CUARENTENA ---\n"
        yield "Metrica,Valor\n"
        yield f'"Eventos totales",{total_limpios + total_sospechosos}\n'
        yield f'"Impactos limpios (contados)",{total_limpios}\n'
        yield f'"Envios apartados (sospechosos)",{total_sospechosos}\n'
        yield "\n"

        # DESGLOSE POR SEÑAL DE SOSPECHA
        yield "--- DESGLOSE POR SEÑAL DE SOSPECHA ---\n"
        yield "Señal,Ocurrencias\n"
        senales_raw = conexion_redis.hgetall("cuarentena:senales")
        for k, v in senales_raw.items():
            yield f'"{k.decode("utf-8")}",{int(v.decode("utf-8"))}\n'
        yield "\n"

        # VOLCADO FORENSE DE LA CUARENTENA (stream crudo, por bloques)
        yield "--- EVENTOS DE CUARENTENA (FORENSE) ---\n"
        yield "Fecha,Hora,Centro,Ubicacion,EmailHash,IP,Sospechoso,Señales\n"
        ultimo_id = "-"
        while True:
            # Leemos el stream en bloques de 500 para no saturar la RAM
            lote = conexion_redis.xrange("cuarentena:eventos", min=ultimo_id, max="+", count=500)
            if not lote:
                break
            for entrada_id, campos in lote:
                d = {k.decode('utf-8'): v.decode('utf-8') for k, v in campos.items()}
                try:
                    dt = datetime.fromtimestamp(int(d.get("ts", 0)))
                    fecha, hora = dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
                except (ValueError, OSError):
                    fecha, hora = "", ""
                sospechoso_txt = "SI" if d.get("sospechoso") == "1" else "NO"
                yield (f'"{fecha}","{hora}","{d.get("centro","")}","{d.get("ubicacion","")}",'
                       f'"{d.get("email_hash","")}","{d.get("ip","")}","{sospechoso_txt}","{d.get("senales","")}"\n')
            # El siguiente bloque empieza justo después del último id leído
            ultimo_id = "(" + lote[-1][0].decode('utf-8')

    return Response(generar_csv(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=estadisticas.csv"})

@admin_bp.route(f"/cerrar-sesion")
@requiere_auth
def admin_cerrar_sesion():
    return Response(
        'Sesión de administrador cerrada correctamente. Por favor, cierra esta pestaña por mayor seguridad.', 401,
        {'WWW-Authenticate': 'Basic realm="Login de Administrador"'}
    )

@admin_bp.route(f"/{os.environ.get('ADMIN_PATH', 'admin-default')}/reset-db", methods=['POST'])
@requiere_auth
def admin_reset_db():
    # ¡ATENCIÓN! Esto borra la base de datos de Redis entera (SOLO para desarrollo)
    conexion_redis.flushdb()
    return redirect(url_for('admin.admin_stats'))