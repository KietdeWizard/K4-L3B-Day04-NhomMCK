# TEAM — Day04, K4-L3B

**Làm nhóm.**

## Thông tin bài nộp

- Tên nhóm: MCK
- Người đại diện / MSSV: Nguyen Minh Kiet / 2A202602373
- Tên repo: K4-L3B-Day04-NhomMCK
- URL repo, nhánh nộp, commit chốt: https://github.com/KietdeWizard/K4-L3B-Day04-NhomMCK
- Deadline áp dụng và link thông báo đổi hạn nếu có: theo hướng dẫn bài lab và thông báo của giảng viên; repo chung được dùng làm bản nộp chính.
- Ghi chú về cộng tác chung trên một laptop: Dao Minh Hieu và Nguyen Minh Kiet cùng thực hiện công việc trên một máy tính, nên các thay đổi được lưu chung trong cùng repository và được coi là đóng góp tập thể trong lịch sử git của repo.

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Nguyen Minh Kiet | 2A202602373 | KietdeWizard | Lead; thiết lập repo, cập nhật prompt, tool, dataset, chạy eval, tổng hợp báo cáo | repo chung / commit tích hợp |
| Dao Minh Hieu | 2A202602561 | daominhhieu | Hỗ trợ cùng làm trên một laptop; kiểm tra prompt, review dữ liệu, hỗ trợ đánh giá kết quả và hoàn thiện báo cáo | repo chung / cộng tác trực tiếp trên cùng máy |

## Nhận xét chung

- Kết quả và bằng chứng: Nhóm đã chuyển domain từ hệ thống helpdesk sang trợ lý theo dõi tuân thủ thuốc, cập nhật prompt/tool, viết lại bộ eval và chạy đánh giá v0/v1. Các bằng chứng nằm trong repository và các file run JSON của mẫu đánh giá.
- Thay đổi hiệu quả nhất: Cập nhật rõ ràng ranh giới an toàn và yêu cầu xác nhận trước khi thay đổi thuốc hoặc thông tin người thân; ép model phải hỏi lại khi thiếu thông tin quan trọng thay vì đoán.
- Giới hạn còn lại: Một số case adversarial vẫn bị fail do mismatch giữa định dạng tool call và cách evaluator kiểm tra; còn cần refinement cho các trường response_type, arg value và ranh giới privacy.
- Cách phân công và tích hợp: Hai thành viên làm việc chung trên cùng một máy tính, nên việc chỉnh sửa và kiểm tra được đồng bộ trong repo. Mỗi thành viên đều có phần đóng góp vào prompt, tool và báo cáo; lịch sử git chung là bằng chứng hợp lệ cho sự cộng tác tập thể.

## INDIVIDUAL


### Dao Minh Hieu — 2A202602561

- Phần việc và file/commit/PR: cùng thực hiện trên cùng một laptop với nhóm trưởng; hỗ trợ kiểm tra lại prompt, review các tool và câu hỏi đánh giá, tham gia chỉnh sửa report và xác nhận các evidence kỹ thuật trong repo chung.
- Quyết định, khó khăn và cách xử lý: cùng hỗ trợ rà soát các case không rõ ràng, kiểm tra lỗi khi model thiếu thông tin hoặc vượt ranh giới hành động. Về mặt hợp tác, vì dùng chung một máy tính nên việc chỉnh sửa được tích hợp liên tục trong repo chung.
- Điều đã học: cần đặt rõ điều kiện hỏi lại, xác nhận và giới hạn của AI trong từng tool; khi xử lý tác dụng phụ hoặc thay đổi thuốc, AI không được tự suy đoán hoặc hành động mà không có xác nhận.
- AI/công cụ đã dùng và cách kiểm tra: cùng sử dụng repo, prompt, tool YAML, dữ liệu eval và các file run JSON; kiểm tra bằng cách đối chiếu hành vi agent với expected tool / expected boundary.
- Thời điểm đã tự nộp URL repo chung trên VLearn: cùng với nhóm khi tiến độ và định dạng bài nộp đã được thống nhất; do cùng máy, việc đồng bộ và xác nhận được thực hiện chung.
