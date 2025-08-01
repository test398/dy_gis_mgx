
class MgxRatingConfig(models.Model):
    mgx_rating_config_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    reference_minimum_score = models.CharField(max_length=255,blank=True, null=True)
    reference_highest_score = models.CharField(max_length=255, blank=True, null=True)
    pid = models.IntegerField(default=0,verbose_name="pid")
    is_score = models.BooleanField(default=False, verbose_name="是否评分")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'mgx_rating_config'
    @property
    def my_values(self):
        return {
            "mgx_rating_config_id": self.mgx_rating_config_id,
            "name": self.name,
            "pid": self.pid,
            "reference_minimum_score": self.reference_minimum_score,
            "reference_highest_score": self.reference_highest_score,
            "is_active": self.is_active,
            "is_score": self.is_score,
            "create_time": self.create_time.strftime('%m/%d/%Y %H:%M:%S') if self.create_time else None,
            "update_time": self.update_time.strftime('%m/%d/%Y %H:%M:%S') if self.update_time else None
        }

class MgxRatingResult(models.Model):
    mgx_rating_result_id = models.AutoField(primary_key=True)
    tq_id = models.CharField(max_length=255, blank=True, null=True)
    result_type = models.IntegerField(blank=True, null=True,verbose_name="治理前/治理后")
    result_content = models.JSONField(blank=True, null=True)
    total_score = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'mgx_rating_result'
    @property
    def my_values(self):
        return {
            "mgx_rating_result_id": self.mgx_rating_result_id,
            "tq_id": self.tq_id,
            "result_type": self.result_type,
            "result_content": self.result_content,
            "total_score": self.total_score,
            "create_time": self.create_time.strftime('%m/%d/%Y %H:%M:%S') if self.create_time else None,
            "update_time": self.update_time.strftime('%m/%d/%Y %H:%M:%S') if self.update_time else None
        }