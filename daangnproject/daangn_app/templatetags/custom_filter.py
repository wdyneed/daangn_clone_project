from django import template

register = template.Library()

# 커스텀 필터 함수 정의
@register.filter(name='custom_filter_name')
def custom_filter(value):
    # 필터 로직을 여기에 구현
    # value를 가공하고 반환
    return transformed_value