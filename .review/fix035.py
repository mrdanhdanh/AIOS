import re

p = "docs/detailtask/T035.md"
s = open(p, encoding="utf-8").read()

# 1. Renumber heading sections N -> N+1 (## 1..12, # 10/11, ### 2.1)
def renum(m):
    h, n, rest = m.group(1), int(m.group(2)), m.group(3)
    return f"{h} {n+1}.{rest}"
s = re.sub(r"^(#{1,3}) (\d+)\.([^\n]*)$",
           lambda m: f"{m.group(1)} {int(m.group(2))+1}.{m.group(3)}", s, flags=re.M)

# 2. Insert Metadata block before the first content section (now ## 2. Mục tiêu)
meta = """## 1. Metadata

* **Milestone:** M7 — Enterprise
* **Task ID:** TASK-035
* **Tên:** Identity + Principal + RBAC/ABAC
* **Mục tiêu canonical:** Xây Identity & Authorization Foundation (Principal → Tenant → Role/Attributes → Action → Resource → Policy → Decision) làm input cho Permission/Policy; không tạo control plane song song.
* **Dependency trực tiếp:** TASK-034 — Doctor + Readiness
* **Task tiếp theo:** TASK-036 — Multi-Tenancy
* **Priority:** Critical
* **Status:** PLANNED
* **Execution model:** Runtime-first · Policy-first · Evidence-first · Fail-closed

"""
s = s.replace("## 2. Mục tiêu", meta + "## 2. Mục tiêu", 1)

# 3. Convert the Acceptance Criteria numbered list into AC-035-NN headings
acs = [
    ("Principal bắt buộc", "Mọi execution hợp lệ đều có `Principal`."),
    ("Principal types", "Principal hỗ trợ `User / Service / Agent / Workflow / System`."),
    ("RBAC deterministic", "RBAC resolve permission deterministic."),
    ("ABAC evaluate", "ABAC evaluate được Subject/Resource/Action/Environment."),
    ("Default deny", "Authorization mặc định **deny** khi thiếu thông tin cần thiết."),
    ("Delegation bound", "Delegation không thể cấp quyền vượt principal."),
    ("No direct storage access", "Agent không truy cập trực tiếp Identity/Role/Policy storage."),
    ("Decision provenance", "Authorization decision có reason + provenance."),
    ("INV-022 enforce", "INV-022 được architecture test enforce."),
    ("Regression M0–M6", "Regression của M0–M6 PASS."),
    ("No parallel control plane", "Không tạo control plane song song."),
    ("Evidence retrievable", "Evidence của các authorization decision có thể truy xuất."),
]
ac_block = "# 12. Acceptance Criteria\n\nTASK-035 chỉ PASS khi:\n\n"
for i, (name, txt) in enumerate(acs, 1):
    ac_block += f"### AC-035-{i:02d} — {name}\n{txt}\n\n"
ac_block += ("Roadmap xác định TASK-035 phải đi **trước TASK-036**, vì Identity + Tenant cần "
             "được đặt trước khi mở rộng execution boundary sang distributed/enterprise runtime. \n")

pat = re.compile(r"# 12\. Acceptance Criteria.*?## 13\. Gate của TASK-035", re.S)
s = pat.sub(ac_block + "## 13. Gate của TASK-035", s, count=1)

open(p, "w", encoding="utf-8").write(s)
print("T035 fixed")
