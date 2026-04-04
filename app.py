from flask import Flask, render_template, request, session
import quiz
from datetime import datetime, timedelta
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = "bookkeeping-app-secret"

history_file = Path("score_history.json")

if history_file.exists():
    with open(history_file, "r", encoding="utf-8") as f:
        score_history = json.load(f)
else:
    score_history = []


@app.route("/", methods=["GET", "POST"])
def home():
    num_questions = 3
    mode = request.form.get("mode") or request.args.get("mode")
    message = None
    review_source_mode = None
    selected = []

    if request.args.get("reset") == "1":
        score_history.clear()
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(score_history, f, ensure_ascii=False, indent=2)

    if request.method == "POST":
        print(request.form)
        mode = request.form.get("mode")
        print("POST mode =", mode)

        if mode == "journal_input":
            selected = quiz.get_questions_by_indices(mode, session.get("question_indices", []))
            score, results = quiz.grade_journal_input(request.form, len(selected), selected)
            total = sum(r["question_max"] for r in results)

        elif mode == "account_only":
            selected = quiz.get_account_only_questions(num_questions)
            score, results = quiz.grade_account_only(request.form, len(selected))
            total = len(selected)

        elif mode == "direction_only":
            selected = quiz.get_direction_only_questions(num_questions)
            score, results = quiz.grade_direction_only(request.form, len(selected))
            total = len(selected)

        elif mode == "trial_balance_direction":
            selected = quiz.get_trial_balance_direction_questions(num_questions)
            score, results = quiz.grade_trial_balance_direction(request.form, len(selected))
            total = len(selected)

        elif mode == "trial_balance_amount":
            selected = quiz.get_trial_balance_amount_questions(num_questions)
            score, results = quiz.grade_trial_balance_amount(request.form, len(selected))
            total = len(selected)

        elif mode == "ledger":
            selected = quiz.get_questions_by_indices(mode, session.get("question_indices", []))
            score, results = quiz.grade_ledger_answers(request.form, len(selected))
            total = sum(r["question_max"] for r in results)

        elif mode == "inventory_gap":
            selected = quiz.inventory_gap_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "inventory_journal_link":
            selected = quiz.inventory_journal_link_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "closing_transfer":
            selected = quiz.closing_transfer_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "bs_pl":
            selected = quiz.bs_pl_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "bs_pl_reason":
            selected = quiz.bs_pl_reason_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "bs_pl_reverse":
            selected = quiz.bs_pl_reverse_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "worksheet_intro":
            selected = quiz.worksheet_intro_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "worksheet_sort":
            selected = quiz.worksheet_sort_questions
            score, results = quiz.grade_worksheet_sort(request.form, len(selected))
            total = len(selected)

        elif mode == "worksheet_amount":
            selected = quiz.worksheet_amount_questions
            score, results = quiz.grade_worksheet_amount(request.form, len(selected))
            total = len(selected)

        elif mode == "adjustment_reason":
            selected = quiz.adjustment_reason_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "adjustment_journal":
            selected = quiz.adjustment_journal_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "worksheet_flow":
            selected = quiz.worksheet_flow_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "worksheet_to_fs":
            selected = quiz.worksheet_to_fs_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "mini_closing":
            selected = quiz.mini_closing_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "bs_or_pl":
            selected = quiz.bs_or_pl_questions
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        elif mode == "review":
            review_source_mode = request.form.get("source_mode", "classification")
            wrong_questions = session.get("wrong_questions", {})
            wrong_dict = wrong_questions.get(review_source_mode, {})

            sorted_items = sorted(wrong_dict.items(), key=lambda x: x[1], reverse=True)
            wrong_texts = [q for q, count in sorted_items]

            selected = quiz.get_review_questions(review_source_mode, wrong_texts)
            selected = selected[:3]

            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        else:
            selected = quiz.get_questions_by_indices(mode, session.get("question_indices", []))
            score, results = quiz.grade_answers(request.form, len(selected))
            total = len(selected)

        # 間違えた問題の index を保存
        if mode in ["classification", "reason", "reverse", "journal", "journal_easy", "journal_hard"]:
            wrong_indices = []
            question_indices = session.get("question_indices", [])

            for i, r in enumerate(results):
                is_correct = r["is_correct"]
                if not is_correct and i < len(question_indices):
                    wrong_indices.append(question_indices[i])

            session["wrong_indices"] = wrong_indices
        else:
            session["wrong_indices"] = []

        score_history.append({
            "score": score,
            "total": total,
            "mode": mode,
            "time": (datetime.utcnow() + timedelta(hours=9)).strftime("%H:%M")        })

        wrong_questions = session.get("wrong_questions", {})

        if mode not in wrong_questions:
            wrong_questions[mode] = {}

        for r in results:
            q_text = r.get("question") or r.get("account") or "問題"
            is_correct = r["is_correct"]

            if not is_correct:
                wrong_questions[mode][q_text] = wrong_questions[mode].get(q_text, 0) + 1

        session["wrong_questions"] = wrong_questions
        print("wrong_questions =", session.get("wrong_questions"))

        if len(score_history) > 10:
            score_history.pop(0)

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(score_history, f, ensure_ascii=False, indent=2)

        display_history = [item for item in score_history if item.get("mode") == mode]
        return render_template(
            "result.html",
            score=score,
            total=total,
            results=results,
            mode=mode,
            history=display_history,
            best_score=max(item["score"] for item in display_history) if display_history else score,
            wrong_indices=session.get("wrong_indices", [])
        )

    if not mode:
        title = "メニューから選択してください"
        session["question_indices"] = []
        return render_template(
            "index.html",
            questions=[],
            mode=None,
            title=title,
            review_source_mode=None,
            message=None,
            auto_jump=False
        )

    # ↓ この下の GET 側の mode_titles 以降はそのままで大丈夫

    mode_titles = {
        "classification": "次の勘定科目がどの分類に属するか選んでください。",
        "reason": "次の説明として最も適切な理由を選んでください。",
        "reverse": "次の説明に当てはまる勘定科目を選んでください。",
        "journal": "次の取引の仕訳として正しいものを選んでください。",
        "journal_easy": "基礎レベルの仕訳問題です。",
        "journal_hard": "応用レベルの仕訳問題です。",
        "journal_input": "仕訳を入力してください（勘定科目は選択、金額は入力）",
        "ledger": "次の仕訳について、どの勘定の借方・貸方に転記されるかを考えてください。",
        "account_only": "この取引で使う勘定科目をすべて選んでください。",
        "direction_only": "それぞれの勘定科目が借方・貸方のどちらにくるか選んでください。",
        "trial_balance_direction": "残高試算表で、その勘定の残高が借方・貸方のどちらに出るか選んでください。",
        "trial_balance_amount": "残高試算表で、その勘定の残高を入力してください。",
        "stock_flow": "次の項目が、期末に引き継がれるのか、リセットされるのかを選んでください。",
        "inventory_gap": "売上原価の考え方を確認しましょう。",
        "inventory_journal_link": "売上原価と仕訳のつながりを確認しましょう。",
        "closing_transfer": "損益振替を確認しましょう。",
        "bs_pl": "各勘定科目が BS / PL のどちらに入るか選んでください。",
        "bs_pl_reason": "BS / PL の理由を確認しましょう。",
        "bs_pl_reverse": "説明から BS / PL 項目を逆引きしましょう。",
        "worksheet_intro": "精算表の意味を確認しましょう。",
        "worksheet_sort": "各勘定科目が精算表で貸借対照表（BS）・損益計算書（PL）のどちらに入るか選んでください。",
        "worksheet_amount": "精算表の金額を考えましょう。",
        "adjustment_reason": "決算整理の理由を確認しましょう。",
        "adjustment_journal": "決算整理仕訳を確認しましょう。",
        "worksheet_flow": "精算表の流れを確認しましょう。",
        "worksheet_to_fs": "精算表から BS / PL への流れを確認しましょう。",
        "mini_closing": "ミニ決算を通して確認しましょう。",
        "bs_or_pl": "この項目が BS / PL のどちらに入るか考えましょう。",
        "review": "復習モード"
    }

    title = mode_titles.get(mode, "")
    selected = []
    message = None
    review_source_mode = None

    if mode == "account_only":
        selected = quiz.get_account_only_questions(num_questions)
        session["question_indices"] = []

    elif mode == "direction_only":
        selected = quiz.get_direction_only_questions(num_questions)
        session["question_indices"] = []

    elif mode == "trial_balance_direction":
        selected = quiz.get_trial_balance_direction_questions(num_questions)
        session["question_indices"] = []

    elif mode == "trial_balance_amount":
        selected = quiz.get_trial_balance_amount_questions(num_questions)
        session["question_indices"] = []

    elif mode == "inventory_gap":
        selected = quiz.inventory_gap_questions
        session["question_indices"] = []

    elif mode == "inventory_journal_link":
        selected = quiz.inventory_journal_link_questions
        session["question_indices"] = []

    elif mode == "closing_transfer":
        selected = quiz.closing_transfer_questions
        session["question_indices"] = []

    elif mode == "bs_pl":
        selected = quiz.bs_pl_questions
        session["question_indices"] = []

    elif mode == "bs_pl_reason":
        selected = quiz.bs_pl_reason_questions
        session["question_indices"] = []

    elif mode == "bs_pl_reverse":
        selected = quiz.bs_pl_reverse_questions
        session["question_indices"] = []

    elif mode == "worksheet_intro":
        selected = quiz.worksheet_intro_questions
        session["question_indices"] = []

    elif mode == "worksheet_sort":
        selected = quiz.worksheet_sort_questions
        session["question_indices"] = []

    elif mode == "worksheet_amount":
        selected = quiz.worksheet_amount_questions
        session["question_indices"] = []

    elif mode == "adjustment_reason":
        selected = quiz.adjustment_reason_questions
        session["question_indices"] = []

    elif mode == "adjustment_journal":
        selected = quiz.adjustment_journal_questions
        session["question_indices"] = []

    elif mode == "worksheet_flow":
        selected = quiz.worksheet_flow_questions
        session["question_indices"] = []

    elif mode == "worksheet_to_fs":
        selected = quiz.worksheet_to_fs_questions
        session["question_indices"] = []

    elif mode == "mini_closing":
        selected = quiz.mini_closing_questions
        session["question_indices"] = []

    elif mode == "bs_or_pl":
        selected = quiz.bs_or_pl_questions
        session["question_indices"] = []

    elif mode == "review":
        review_source_mode = request.args.get("source", "classification")
        wrong_questions = session.get("wrong_questions", {})
        wrong_dict = wrong_questions.get(review_source_mode, {})
        message = None

        # 間違えた回数が多い順に並べる
        sorted_items = sorted(wrong_dict.items(), key=lambda x: x[1], reverse=True)
        wrong_texts = [q for q, count in sorted_items]

        print("review_source_mode =", review_source_mode)
        print("wrong_texts =", wrong_texts)

        selected = quiz.get_review_questions(review_source_mode, wrong_texts)

        print("review selected =", selected)
        print("review selected count =", len(selected))

        if not selected:
            selected = []
            message = "このモードでは、まだ復習する問題がありません。"
        else:
            selected = selected[:3]

        title = "復習モード"
        session["question_indices"] = []

    else:
        retry = request.args.get("retry_wrong")

        if retry == "1" and session.get("wrong_indices"):
            indices = session["wrong_indices"]
            selected = quiz.get_questions_by_indices(mode, indices)
            session["question_indices"] = indices
        else:
            selected, indices = quiz.get_questions_with_indices(mode, num_questions)
            session["question_indices"] = indices

    auto_jump = True

    return render_template(
        "index.html",
        questions=selected,
        mode=mode,
        title=title,
        review_source_mode=review_source_mode if mode == "review" else None,
        message=message if mode == "review" else None,
        auto_jump=auto_jump
    )
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
