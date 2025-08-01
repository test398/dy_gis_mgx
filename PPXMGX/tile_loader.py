import copy
import json

class DedupedRequest:
    def __init__(self):
        self.entries = {}
    def request(self, key, meta, callback):
        # 这里只模拟直接调用callback，实际可加并发/去重逻辑
        callback_func = callback
        # 返回一个可取消的对象
        class CancelObj:
            def cancel(self):
                pass
        return CancelObj()

def load_tile(tile, callback, loader_instance):
    """
    Python版loadTile函数，模拟JS逻辑
    :param tile: dict，包含uid, request, tileID等
    :param callback: 回调函数，参数为(error, result)
    :param loader_instance: 类似JS中的this，需有loadVectorData方法、属性等
    """
    r = tile['uid']
    n = tile.get('request')
    i = n.get('collectResourceTiming') if n else None
    s = loader_instance.loading[r] = loader_instance.TileClass(tile)  # 假设TileClass为um类的Python实现

    def on_vector_data(a, o):
        l = r not in loader_instance.loading
        if r in loader_instance.loading:
            del loader_instance.loading[r]
        if l or a or not o:
            s.status = 'done'
            if not l:
                loader_instance.loaded[r] = s
            callback(a)
            return
        u = o['rawData']
        c = {}
        if 'expires' in o:
            c['expires'] = o['expires']
        if 'cacheControl' in o:
            c['cacheControl'] = o['cacheControl']
        tileID = tile['tileID']
        canonical = tileID['canonical']
        reference = tileID.get('reference')
        _tileY = tileID.get('_tileY')
        _tileH = tileID.get('_tileH')
        x = canonical['x']
        y = canonical['y']
        z = canonical['z']
        # 构造VectorTile对象
        s.vectorTile = o.get('vectorTile') or loader_instance.VectorTileClass(loader_instance.PBFClass(u), None, {
            'reference': reference,
            '_tileY': _tileY,
            '_tileH': _tileH,
            'x': x,
            'y': y,
            'z': z
        })
        print('vectorTile内容:', s.vectorTile)
        # 后续解析逻辑可继续补充
        # ...
        # 这里只回调一次，模拟e(null, ...)
        callback(None, {'vectorTile': s.vectorTile, 'rawData': u, **c})

    # 调用loadVectorData
    s.abort = loader_instance.loadVectorData(tile, on_vector_data)
    # 这里省略了isSpriteLoaded等异步调度逻辑
    return s

def pm(t, e, r, self_obj):
    """
    Python版pm函数，模拟JS逻辑
    :param t: dict，包含request, data, tileID, isSymbolTile, tileZoom等
    :param e: 回调函数，参数为(error, result)
    :param r: bool，控制是否返回vectorTile
    :param self_obj: 需有deduped属性（DedupedRequest实例）
    """
    n = json.dumps(t['request'])
    # 如果有data，直接缓存
    if 'data' in t and t['data']:
        self_obj.deduped.entries[n] = {'result': [None, t['data']]}
    
    def inner_callback(cb):
        def vt_callback(n, i, s, a):
            if n:
                cb(n)
            elif i:
                tileID = t['tileID']
                canonical = tileID['canonical']
                reference = tileID.get('reference')
                _tileY = tileID.get('_tileY')
                _tileH = tileID.get('_tileH')
                x = canonical['x']
                y = canonical['y']
                z = canonical['z']
                result = {
                    'vectorTile': None if r else self_obj.VectorTileClass(self_obj.PBFClass(i), None, {
                        'reference': reference,
                        '_tileY': _tileY,
                        '_tileH': _tileH,
                        'x': x,
                        'y': y,
                        'z': z
                    }),
                    'rawData': i,
                    'cacheControl': s,
                    'expires': a
                }
                cb(None, result)
        # Vt为解码函数，需实现
        self_obj.Vt(t['request'], vt_callback)
        def cancel():
            pass
        return cancel
    # 调用deduped.request
    return self_obj.deduped.request(n, {
        'type': 'parseTile',
        'isSymbolTile': t.get('isSymbolTile'),
        'zoom': t.get('tileZoom')
    }, inner_callback(e))

# 你需要实现或传入TileClass、VectorTileClass、PBFClass等Python类，并补充loader_instance的相关属性和方法。 
# 你需要实现或传入VectorTileClass、PBFClass、Vt等Python类/方法，并补充self_obj的相关属性。 