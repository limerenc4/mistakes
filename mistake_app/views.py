# mistake_app/views.py
from django.shortcuts import render, redirect
from django.db.models import Count
from .models import Mistake
import json
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
from datetime import datetime,timedelta

# 科目颜色配置
SUBJECT_COLORS = {
    'chinese': '#FF6666',
    'math': '#4dc9f6',
    'english': '#f67019',
    'physics': '#f53794',
    'chemistry': '#537bc4',
    'biology': '#acc236',
    'history': '#166a8f',
    'geography': '#00cc99',
    'politics': '#9966ff'
}

def home(request):
    """ 主页视图 """
    # 统计数据处理
    raw_stats = Mistake.objects.values('subject').annotate(total=Count('id'))
    subject_dict = dict(Mistake.SUBJECT_CHOICES)
    
    stats = []
    for item in raw_stats:
        stats.append({
            'name': subject_dict.get(item['subject'], '其他科目'),
            'count': item['total'],
            'color': SUBJECT_COLORS.get(item['subject'], '#cccccc')
        })
    
    # 最新错题
    latest_mistakes = Mistake.objects.all()[:5]
    
    return render(request, 'home.html', {
        'stats_json': json.dumps(stats, ensure_ascii=False),
        'latest_mistakes': latest_mistakes,
        'subject_choices': Mistake.SUBJECT_CHOICES
    })

def add_mistake(request):
    if request.method == 'POST':
        try:
            # 创建对象时包含文件字段
            new_mistake = Mistake.objects.create(
                question=request.POST['question'],
                wrong_answer=request.POST['wrong_answer'],
                right_answer=request.POST['right_answer'],
                subject=request.POST['subject'],
                question_image=request.FILES.get('question_image')  # 获取上传文件
            )
            return redirect('home')
        except Exception as e:
            print(f"保存出错: {e}")
            return render(request, 'add.html', {
                'error_message': '保存失败，请检查图片格式和大小',
                'subject_choices': Mistake.SUBJECT_CHOICES
            })
    
    return render(request, 'add.html', {
        'subject_choices': Mistake.SUBJECT_CHOICES
    })

def mistake_list(request):
     # 获取排序后的全部数据
    mistakes_list = Mistake.objects.all().order_by('-add_date')
    
    # 分页配置
    paginator = Paginator(mistakes_list, 10)  # 每页10条
    page_number = request.GET.get('page', 1)  # 添加默认值
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return render(request, 'list.html', {
        'page_obj': page_obj,          # 分页对象
        'mistakes': page_obj.object_list,  # 当前页数据
        'subject_choices': Mistake.SUBJECT_CHOICES
    })
def statistics(request):
    """ 统计视图 """
    stats = Mistake.objects.values('subject').annotate(
        total=Count('id'),
        latest=Max('add_date')
    )
    return render(request, 'stats.html', {
        'stats': stats,
        'subject_choices': Mistake.SUBJECT_CHOICES
    })
def export_page(request):
    """ 导出设置页面 """
    return render(request, 'export.html', {
        'subject_choices': Mistake.SUBJECT_CHOICES,
        'date_ranges': [
            ('all', '全部时间'),
            ('week', '最近一周'),
            ('month', '最近一月')
        ]
    })

def export_data(request):
    """ 处理导出请求 """
    # 获取参数
    export_format = request.GET.get('format', 'csv')
    subject = request.GET.get('subject', 'all')
    date_range = request.GET.get('range', 'all')
    
    # 构建查询集
    queryset = Mistake.objects.all()
    
    # 科目筛选
    if subject != 'all':
        queryset = queryset.filter(subject=subject)
    
    # 时间筛选
    if date_range == 'week':
        queryset = queryset.filter(add_date__gte=datetime.now()-timedelta(days=7))
    elif date_range == 'month':
        queryset = queryset.filter(add_date__gte=datetime.now()-timedelta(days=30))
    
    # 处理不同格式
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        filename = f"mistakes_{datetime.now().strftime('%Y%m%d')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['题目', '错误答案', '正确答案', '科目', '错误次数', '添加时间'])
        
        for obj in queryset:
            writer.writerow([
                obj.question,
                obj.wrong_answer,
                obj.right_answer,
                obj.get_subject_display(),
                obj.error_count,
                obj.add_date.strftime("%Y-%m-%d %H:%M")
            ])
            
        return response
    
    return HttpResponse("暂不支持该格式", status=400)