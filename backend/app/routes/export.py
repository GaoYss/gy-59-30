import csv
import io
from datetime import datetime

from flask import Blueprint, make_response, request

from ..models import Appointment, ExamRecord, Makeup

export_bp = Blueprint("export", __name__, url_prefix="/api/export")


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def make_csv_response(rows, headers, filename):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    output.seek(0)

    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}.csv"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@export_bp.get("/appointments")
def export_appointments():
    start_date = parse_date(request.args.get("startDate"))
    end_date = parse_date(request.args.get("endDate"))

    query = Appointment.query.order_by(Appointment.exam_date.asc(), Appointment.timeslot.asc())

    if start_date:
        query = query.filter(Appointment.exam_date >= start_date)
    if end_date:
        query = query.filter(Appointment.exam_date <= end_date)

    items = query.all()

    rows = []
    for item in items:
        rows.append([
            item.id,
            item.student_name,
            item.id_number,
            item.subject,
            item.exam_date.isoformat(),
            item.timeslot,
            item.status,
            item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    headers = ["ID", "学员姓名", "证件号", "科目", "考试日期", "时段", "状态", "创建时间"]
    filename = f"预约记录_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return make_csv_response(rows, headers, filename)


@export_bp.get("/scores")
def export_scores():
    start_date = parse_date(request.args.get("startDate"))
    end_date = parse_date(request.args.get("endDate"))

    query = ExamRecord.query.order_by(ExamRecord.submitted_at.desc())

    if start_date:
        query = query.filter(ExamRecord.submitted_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(ExamRecord.submitted_at <= datetime.combine(end_date, datetime.max.time()))

    items = query.all()

    rows = []
    for item in items:
        rows.append([
            item.id,
            item.student_name,
            item.subject,
            item.score,
            item.total_questions,
            item.correct_count,
            "合格" if item.passed else "不合格",
            item.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    headers = ["ID", "学员姓名", "科目", "分数", "总题数", "答对数", "结果", "提交时间"]
    filename = f"成绩记录_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return make_csv_response(rows, headers, filename)


@export_bp.get("/makeups")
def export_makeups():
    start_date = parse_date(request.args.get("startDate"))
    end_date = parse_date(request.args.get("endDate"))

    query = Makeup.query.order_by(Makeup.created_at.desc())

    if start_date:
        query = query.filter(Makeup.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Makeup.created_at <= datetime.combine(end_date, datetime.max.time()))

    items = query.all()

    rows = []
    for item in items:
        rows.append([
            item.id,
            item.student_name,
            item.original_subject,
            item.failed_score,
            item.scheduled_date.isoformat() if item.scheduled_date else "",
            item.status,
            item.notes or "",
            item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    headers = ["ID", "学员姓名", "原科目", "失败分数", "补考日期", "状态", "备注", "创建时间"]
    filename = f"补考记录_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return make_csv_response(rows, headers, filename)


@export_bp.get("/statistics")
def export_statistics():
    start_date = parse_date(request.args.get("startDate"))
    end_date = parse_date(request.args.get("endDate"))

    appointment_query = Appointment.query
    score_query = ExamRecord.query
    makeup_query = Makeup.query

    if start_date:
        appointment_query = appointment_query.filter(Appointment.exam_date >= start_date)
        score_query = score_query.filter(ExamRecord.submitted_at >= datetime.combine(start_date, datetime.min.time()))
        makeup_query = makeup_query.filter(Makeup.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        appointment_query = appointment_query.filter(Appointment.exam_date <= end_date)
        score_query = score_query.filter(ExamRecord.submitted_at <= datetime.combine(end_date, datetime.max.time()))
        makeup_query = makeup_query.filter(Makeup.created_at <= datetime.combine(end_date, datetime.max.time()))

    total_appointments = appointment_query.count()
    total_scores = score_query.count()
    total_makeups = makeup_query.count()

    passed_scores = score_query.filter_by(passed=True).count()
    pass_rate = (passed_scores / total_scores * 100) if total_scores > 0 else 0

    appointments_by_subject = {}
    for item in appointment_query.all():
        appointments_by_subject[item.subject] = appointments_by_subject.get(item.subject, 0) + 1

    scores_by_subject = {}
    passed_by_subject = {}
    for item in score_query.all():
        scores_by_subject[item.subject] = scores_by_subject.get(item.subject, 0) + 1
        if item.passed:
            passed_by_subject[item.subject] = passed_by_subject.get(item.subject, 0) + 1

    makeup_by_status = {}
    for item in makeup_query.all():
        makeup_by_status[item.status] = makeup_by_status.get(item.status, 0) + 1

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["统计报表"])
    writer.writerow([f"统计周期：{start_date or '开始'} 至 {end_date or '至今'}"])
    writer.writerow([f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    writer.writerow([])

    writer.writerow(["总览统计"])
    writer.writerow(["指标", "数量"])
    writer.writerow(["预约总数", total_appointments])
    writer.writerow(["考试总数", total_scores])
    writer.writerow(["补考总数", total_makeups])
    writer.writerow(["合格人数", passed_scores])
    writer.writerow(["合格率(%)", f"{pass_rate:.2f}"])
    writer.writerow([])

    writer.writerow(["预约 - 按科目统计"])
    writer.writerow(["科目", "预约数"])
    for subject, count in sorted(appointments_by_subject.items()):
        writer.writerow([subject, count])
    writer.writerow([])

    writer.writerow(["成绩 - 按科目统计"])
    writer.writerow(["科目", "考试数", "合格数", "合格率(%)"])
    for subject in sorted(scores_by_subject.keys()):
        total = scores_by_subject[subject]
        passed = passed_by_subject.get(subject, 0)
        rate = (passed / total * 100) if total > 0 else 0
        writer.writerow([subject, total, passed, f"{rate:.2f}"])
    writer.writerow([])

    writer.writerow(["补考 - 按状态统计"])
    writer.writerow(["状态", "数量"])
    for status, count in sorted(makeup_by_status.items()):
        writer.writerow([status, count])

    output.seek(0)

    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    filename = f"统计报表_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}.csv"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
