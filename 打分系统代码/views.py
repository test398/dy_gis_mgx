
def get_mgx_rating_list(request):
    if request.method != 'POST':
        return JsonResponse({"code": 404, "msg": "Not Found"})
    try:
        res_list = MgxRatingConfig.objects.filter(is_active=True).all().order_by('mgx_rating_config_id')
        res_list_ract = [i.my_values for i in res_list if i is not None]
        res_tree = TreeUtils.build_tree(res_list_ract, 'mgx_rating_config_id', 'pid')

        return JsonResponse({
            "code": 200,
            "msg": "Success",
            "data": res_tree
        })
    except Exception as e:
        return JsonResponse({"code": 500, "msg": str(e)})


def save_mgx_rating_config(request):
    if request.method != 'POST':
        return JsonResponse({"code": 404, "msg": "Not Found"})
    try:
        data = json.loads(request.body)
        mgx_rating_config_id = data.get("mgx_rating_config_id", None)
        name = data.get("name", None)
        pid = data.get("pid", 0)
        reference_minimum_score = data.get("reference_minimum_score", 0)
        reference_highest_score = data.get("reference_highest_score", 0)
        is_active = data.get("is_active", False)
        is_score = data.get("is_score", False)
        is_delete = data.get("is_delete", False)
        if mgx_rating_config_id is not None:
            if is_delete:
                has_child = MgxRatingConfig.objects.filter(pid=mgx_rating_config_id).exists()
                if has_child:
                    return JsonResponse({"code": 400, "msg": "Cannot delete this rating config because it has child configs."})
                MgxRatingConfig.objects.filter(mgx_rating_config_id=mgx_rating_config_id).delete()
            else:
                MgxRatingConfig.objects.filter(mgx_rating_config_id=mgx_rating_config_id).update(is_score=is_score,is_active=is_active,name=name, pid=pid, reference_minimum_score=reference_minimum_score,reference_highest_score=reference_highest_score)
        else:
            MgxRatingConfig.objects.create(is_score=is_score,is_active=is_active,name=name, pid=pid, reference_minimum_score=reference_minimum_score,reference_highest_score=reference_highest_score)
        return JsonResponse({
            "code": 200,
            "msg": "Success",
            "data": {}
        })
    except Exception as e:
        return JsonResponse({"code": 500, "msg": str(e)})

def get_mgx_rating_config_by_id(request):
    if request.method != 'POST':
        return JsonResponse({"code": 404, "msg": "Not Found"})
    try:
        data = json.loads(request.body)
        mgx_rating_config_id = data.get("mgx_rating_config_id", None)
        if not mgx_rating_config_id:
            return JsonResponse({"code": 404, "msg": "Parameter error"})
        res = MgxRatingConfig.objects.filter(mgx_rating_config_id=mgx_rating_config_id).first()
        return JsonResponse({
            "code": 200,
            "msg": "Success",
            "data": res.my_values if res else {}
        })
    except Exception as e:
        return JsonResponse({"code": 500, "msg": str(e)})

def save_max_rating_result(request):
    if request.method != 'POST':
        return JsonResponse({"code": 404, "msg": "Not Found"})
    try:
        data = json.loads(request.body)
        mgx_rating_result_id = data.get("mgx_rating_result_id", None)
        tq_id = data.get("tq_id", "").strip()
        result_content = data.get('result_content', None)
        result_type = int(data.get('result_type', 0))
        total_score = int(data.get("total_score", 0))
        is_delete = data.get("is_delete", False)
        if mgx_rating_result_id is not None:
            if is_delete:
                MgxRatingResult.objects.filter(mgx_rating_result_id=mgx_rating_result_id).delete()
                return JsonResponse({"code": 200, "msg": "Deleted successfully", "data": {}})
            MgxRatingResult.objects.filter(mgx_rating_result_id=mgx_rating_result_id).update(
                tq_id=tq_id,
                result_content=result_content,
                result_type=result_type,
                total_score=total_score,
            )
        else:
            MgxRatingResult.objects.create(
                tq_id=tq_id,
                result_content=result_content,
                result_type=result_type,
                total_score=total_score,
            )
        return JsonResponse({
            "code": 200,
            "msg": "Success",
            "data": {}
        })
    except Exception as e:
        return JsonResponse({"code": 500, "msg": str(e)})


def get_max_rating_result_list(request):
    if request.method != 'POST':
        return JsonResponse({"code": 404, "msg": "Not Found"})
    try:
        data = json.loads(request.body)
        page_num = data.get("pageNum", 1)
        page_size = data.get("pageSize", 10)
        tq_id = data.get("tq_id", "").strip()
        if tq_id:
            queryset = MgxRatingResult.objects.filter(tq_id__icontains=tq_id).all().order_by('-create_time')
        else:
            queryset = MgxRatingResult.objects.all().order_by('-create_time')
        pagination_data = paginate_queryset_utils(queryset, page_num, page_size)
        ser = MgxRatingResultSerializer(pagination_data["data"], many=True)
        return JsonResponse({
            "code": 200,
            "msg": "Success",
            "total": pagination_data["total"],
            "totalPages": pagination_data["totalPages"],
            "pageNum": pagination_data["pageNum"],
            "pageSize": pagination_data["pageSize"],
            "data": ser.data
        })
    except Exception as e:
        return JsonResponse({"code": 400, "msg": str(e)})