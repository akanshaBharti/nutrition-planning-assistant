import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api';

const today = () => new Date().toISOString().slice(0, 10);

function toDisplayDate(value) {
  if (!value) return '';
  const [year, month, day] = value.split('-');
  return year && month && day ? `${day}-${month}-${year}` : value;
}

function toIsoDate(value) {
  const match = /^(\d{2})-(\d{2})-(\d{4})$/.exec(value.trim());
  if (!match) return null;
  const [, day, month, year] = match;
  return `${year}-${month}-${day}`;
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
}

function toList(value) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function listText(value) {
  return Array.isArray(value) ? value.join(', ') : '';
}

function App() {
  const [profile, setProfile] = useState(null);
  const [daily, setDaily] = useState(null);
  const [plans, setPlans] = useState([]);
  const [historyData, setHistoryData] = useState({ meals: [], corrections: [] });
  const [review, setReview] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [mealText, setMealText] = useState('2 boiled eggs, 1 cup cooked rice, grilled chicken 150g');
  const [mealType, setMealType] = useState('lunch');
  const [activeDate, setActiveDate] = useState(today());
  const [activeDateText, setActiveDateText] = useState(toDisplayDate(today()));
  const [activeTab, setActiveTab] = useState('tracker');

  const remainingCalories = useMemo(() => {
    if (!profile || !daily) return 0;
    return Number(profile.calorie_target) - Number(daily.total_calories || 0);
  }, [profile, daily]);

  const approvedPlans = useMemo(
    () => plans.filter((plan) => plan.status === 'approved'),
    [plans]
  );

  async function refresh() {
    const [profileData, dailyData, planData, history] = await Promise.all([
      api('/profile/'),
      api(`/meals/daily/?date=${activeDate}`),
      api('/plans/'),
      api('/meals/history/'),
    ]);
    setProfile(profileData);
    setDaily(dailyData);
    setPlans(planData);
    setHistoryData(history);
  }

  useEffect(() => {
    refresh().catch((error) => setMessage(error.message));
  }, [activeDate]);

  function updateActiveDate(value) {
    setActiveDateText(value);
    const isoDate = toIsoDate(value);
    if (isoDate) {
      setActiveDate(isoDate);
    }
  }

  async function saveProfile(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setLoading(true);
    try {
      const payload = {
        calorie_target: Number(form.get('calorie_target')),
        dietary_preferences: toList(form.get('dietary_preferences') || ''),
        allergies: toList(form.get('allergies') || ''),
        foods_to_avoid: toList(form.get('foods_to_avoid') || ''),
      };
      setProfile(await api('/profile/', { method: 'POST', body: JSON.stringify(payload) }));
      setMessage('Profile saved.');
      await refresh();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function extractMeal(event) {
    event.preventDefault();
    setLoading(true);
    try {
      const data = await api('/meals/extract/', {
        method: 'POST',
        body: JSON.stringify({ description: mealText, date: activeDate, meal_type: mealType }),
      });
      setReview(data);
      setMessage(data.requires_clarification ? 'Please review the clarification notes before saving.' : 'Meal extracted from the knowledge base.');
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  function updateReviewItem(index, field, value) {
    setReview((current) => {
      const items = current.items.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [field]: value } : item
      );
      const total = items.reduce((sum, item) => sum + Number(item.user_calories || item.estimated_calories || 0), 0);
      return { ...current, items, total_calories: total.toFixed(2) };
    });
  }

  async function saveMeal() {
    setLoading(true);
    try {
      const saved = await api('/meals/save/', { method: 'POST', body: JSON.stringify(review) });
      setReview(null);
      setMessage(`Saved meal with ${saved.total_calories} kcal.`);
      await refresh();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function generatePlan() {
    setLoading(true);
    try {
      const plan = await api('/plans/generate/', { method: 'POST', body: JSON.stringify({}) });
      setPlans((current) => [plan, ...current]);
      setMessage('Generated a draft plan for tomorrow.');
      await refresh();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function updatePlanStatus(planId, action) {
    setLoading(true);
    try {
      const plan = await api(`/plans/${planId}/${action}/`, { method: 'POST', body: JSON.stringify({}) });
      setPlans((current) => current.map((item) => (item.id === plan.id ? plan : item)));
      setMessage(`Plan ${action === 'approve' ? 'approved' : 'rejected'}.`);
      await refresh();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">Knowledge-grounded wellness tracker</p>
          <h1>Nutrition Planning Assistant</h1>
        </div>
        <div className="date-control">
          <label htmlFor="activeDate">Daily view</label>
          <input
            id="activeDate"
            type="text"
            inputMode="numeric"
            pattern="\d{2}-\d{2}-\d{4}"
            placeholder="DD-MM-YYYY"
            value={activeDateText}
            onChange={(event) => updateActiveDate(event.target.value)}
          />
        </div>
      </section>

      <p className="disclaimer">
        General wellness tracking only. This app does not provide medical diagnosis, treatment, or guaranteed health outcomes.
      </p>

      {message && <div className="notice">{message}</div>}

      <nav className="tabs" aria-label="Wellness workspace views">
        <button className={activeTab === 'tracker' ? 'active' : ''} onClick={() => setActiveTab('tracker')}>Tracker</button>
        <button className={activeTab === 'saved' ? 'active' : ''} onClick={() => setActiveTab('saved')}>Saved History</button>
      </nav>

      {activeTab === 'tracker' && (
        <>
          <div className="workspace-grid">
            <section className="panel">
              <h2>Profile</h2>
              {profile && (
                <form onSubmit={saveProfile} className="form-grid">
                  <label>
                    Calorie target
                    <input name="calorie_target" type="number" min="1" defaultValue={profile.calorie_target} />
                  </label>
                  <label>
                    Dietary preferences
                    <input name="dietary_preferences" defaultValue={listText(profile.dietary_preferences)} placeholder="vegetarian, high-protein" />
                  </label>
                  <label>
                    Allergies
                    <input name="allergies" defaultValue={listText(profile.allergies)} placeholder="peanut, milk" />
                  </label>
                  <label>
                    Foods to avoid
                    <input name="foods_to_avoid" defaultValue={listText(profile.foods_to_avoid)} placeholder="fried chicken" />
                  </label>
                  <button disabled={loading}>Save Profile</button>
                </form>
              )}
            </section>

            <section className="panel">
              <h2>Record Meal</h2>
              <form onSubmit={extractMeal} className="form-grid">
                <label>
                  Meal type
                  <select value={mealType} onChange={(event) => setMealType(event.target.value)}>
                    <option value="breakfast">Breakfast</option>
                    <option value="lunch">Lunch</option>
                    <option value="dinner">Dinner</option>
                    <option value="snack">Snack</option>
                    <option value="other">Other</option>
                  </select>
                </label>
                <label>
                  Supported text format
                  <textarea value={mealText} onChange={(event) => setMealText(event.target.value)} rows="5" />
                </label>
                <button disabled={loading}>Extract Food Items</button>
              </form>
            </section>

            <section className="panel daily-panel">
              <h2>Daily Intake</h2>
              <div className="meter">
                <span style={{ width: `${Math.min(100, ((daily?.total_calories || 0) / (profile?.calorie_target || 1)) * 100)}%` }} />
              </div>
              <div className="stats">
                <strong>{Number(daily?.total_calories || 0).toFixed(0)} kcal</strong>
                <span>{remainingCalories >= 0 ? `${remainingCalories.toFixed(0)} remaining` : `${Math.abs(remainingCalories).toFixed(0)} over target`}</span>
              </div>
              <div className="history">
                {(daily?.meals || []).map((meal) => (
                  <article key={meal.id} className="row-card">
                    <div>
                      <strong>{meal.meal_type}</strong>
                      <p>{meal.original_text}</p>
                    </div>
                    <span>{Number(meal.total_calories).toFixed(0)} kcal</span>
                  </article>
                ))}
                {daily?.meals?.length === 0 && <p className="muted">No meals saved for this date.</p>}
              </div>
            </section>
          </div>

          {review && (
            <section className="panel wide">
              <div className="section-heading">
                <div>
                  <h2>Review Meal Before Saving</h2>
                  <p>Calories come from documented KB entries. Edit any estimate before saving.</p>
                </div>
                <button className="secondary" onClick={() => setReview(null)}>Discard</button>
              </div>

              {review.clarification_questions?.length > 0 && (
                <div className="warning-list">
                  {review.clarification_questions.map((question) => <p key={question}>{question}</p>)}
                </div>
              )}

              <div className="review-table">
                <div className="table-head">
                  <span>Food</span>
                  <span>Qty</span>
                  <span>Method</span>
                  <span>Estimate</span>
                  <span>Nutrition</span>
                  <span>Your calories</span>
                </div>
                {review.items.map((item, index) => (
                  <div className="table-row" key={`${item.food_name}-${index}`}>
                    <input value={item.food_name} onChange={(event) => updateReviewItem(index, 'food_name', event.target.value)} />
                    <div className="inline-inputs">
                      <input type="number" value={item.quantity || ''} onChange={(event) => updateReviewItem(index, 'quantity', event.target.value)} />
                      <input value={item.unit || ''} onChange={(event) => updateReviewItem(index, 'unit', event.target.value)} />
                    </div>
                    <input value={item.preparation_method || ''} onChange={(event) => updateReviewItem(index, 'preparation_method', event.target.value)} />
                    <span>{Number(item.estimated_calories || 0).toFixed(0)} kcal</span>
                    <div className="macro-inputs" aria-label={`Nutrition estimates for ${item.food_name}`}>
                      <label>
                        Protein
                        <input type="number" min="0" step="0.1" value={item.protein_g || ''} onChange={(event) => updateReviewItem(index, 'protein_g', event.target.value)} />
                      </label>
                      <label>
                        Carbs
                        <input type="number" min="0" step="0.1" value={item.carbs_g || ''} onChange={(event) => updateReviewItem(index, 'carbs_g', event.target.value)} />
                      </label>
                      <label>
                        Fat
                        <input type="number" min="0" step="0.1" value={item.fat_g || ''} onChange={(event) => updateReviewItem(index, 'fat_g', event.target.value)} />
                      </label>
                    </div>
                    <input type="number" value={item.user_calories || ''} placeholder="Optional" onChange={(event) => updateReviewItem(index, 'user_calories', event.target.value)} />
                    <p className="source-line">{item.source || item.uncertainty}</p>
                  </div>
                ))}
              </div>

              <div className="review-footer">
                <span>Total: {Number(review.total_calories || 0).toFixed(0)} kcal</span>
                <button onClick={saveMeal} disabled={loading}>Save Meal</button>
              </div>
            </section>
          )}

          <section className="panel wide">
            <div className="section-heading">
              <div>
                <h2>Next-Day Meal Plan</h2>
                <p>Drafts use saved preferences, allergies, avoided foods, and documented nutrition values.</p>
              </div>
              <button onClick={generatePlan} disabled={loading}>Generate Plan</button>
            </div>

            <div className="plan-grid">
              {plans.map((plan) => (
                <article className="plan-card" key={plan.id}>
                  <div className="plan-head">
                    <div>
                      <strong>{toDisplayDate(plan.target_date)}</strong>
                      <p>{Number(plan.total_calories).toFixed(0)} kcal</p>
                    </div>
                    <span className={`status ${plan.status}`}>{plan.status}</span>
                  </div>
                  <div className="plan-items">
                    {plan.items.map((item) => (
                      <div key={item.id} className="plan-item">
                        <span>{item.meal_type}</span>
                        <strong>{item.quantity} {item.unit} {item.food_name}</strong>
                        <em>{Number(item.calories).toFixed(0)} kcal</em>
                      </div>
                    ))}
                  </div>
                  <div className="assumptions">
                    {[...(plan.restrictions_applied || []), ...(plan.assumptions || [])].map((item) => <p key={item}>{item}</p>)}
                  </div>
                  {plan.status === 'draft' && (
                    <div className="button-row">
                      <button onClick={() => updatePlanStatus(plan.id, 'approve')}>Approve</button>
                      <button className="secondary" onClick={() => updatePlanStatus(plan.id, 'reject')}>Reject</button>
                    </div>
                  )}
                </article>
              ))}
              {plans.length === 0 && <p className="muted">No meal plans yet.</p>}
            </div>
          </section>
        </>
      )}

      {activeTab === 'saved' && (
        <section className="saved-grid">
          <div className="panel">
            <h2>Meal History</h2>
            <div className="history">
              {historyData.meals.map((meal) => (
                <article key={meal.id} className="row-card stacked">
                  <div>
                    <strong>{toDisplayDate(meal.date)} - {meal.meal_type}</strong>
                    <p>{meal.original_text}</p>
                  </div>
                  <span>{Number(meal.total_calories).toFixed(0)} kcal</span>
                </article>
              ))}
              {historyData.meals.length === 0 && <p className="muted">No saved meals yet.</p>}
            </div>
          </div>

          <div className="panel">
            <h2>User Corrections</h2>
            <div className="history">
              {historyData.corrections.map((correction) => (
                <article key={correction.id} className="row-card stacked">
                  <div>
                    <strong>{correction.food_name}</strong>
                    <p>{toDisplayDate(correction.meal_date)} - {correction.meal_type}</p>
                  </div>
                  <span>{Number(correction.original_calories).toFixed(0)} to {Number(correction.corrected_calories).toFixed(0)} kcal</span>
                </article>
              ))}
              {historyData.corrections.length === 0 && <p className="muted">No calorie corrections saved yet.</p>}
            </div>
          </div>

          <div className="panel">
            <h2>Approved Plans</h2>
            <div className="plan-grid compact">
              {approvedPlans.map((plan) => (
                <article className="plan-card" key={plan.id}>
                  <div className="plan-head">
                    <div>
                      <strong>{toDisplayDate(plan.target_date)}</strong>
                      <p>{Number(plan.total_calories).toFixed(0)} kcal</p>
                    </div>
                    <span className="status approved">approved</span>
                  </div>
                  <div className="plan-items">
                    {plan.items.map((item) => (
                      <div key={item.id} className="plan-item">
                        <span>{item.meal_type}</span>
                        <strong>{item.quantity} {item.unit} {item.food_name}</strong>
                        <em>{Number(item.calories).toFixed(0)} kcal</em>
                      </div>
                    ))}
                  </div>
                </article>
              ))}
              {approvedPlans.length === 0 && <p className="muted">No approved plans yet.</p>}
            </div>
          </div>
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
