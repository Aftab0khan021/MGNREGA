import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { axiosInstance } from "../App";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  ArrowLeft,
  Users,
  Calendar,
  Wallet,
  Briefcase,
  TrendingUp,
  TrendingDown,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { toast } from "sonner";

const DashboardPage = () => {
  const { districtCode } = useParams();
  const navigate = useNavigate();
  const [language, setLanguage] = useState("en");
  const [translations, setTranslations] = useState({});
  const [performances, setPerformances] = useState([]);
  const [currentPerformance, setCurrentPerformance] = useState(null);
  const [previousPerformance, setPreviousPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    loadTranslations();
    loadPerformanceData();
  }, [language, districtCode]);

  const loadTranslations = async () => {
    try {
      const response = await axiosInstance.get(`/translations/${language}`);
      setTranslations(response.data);
    } catch (error) {
      console.error("Failed to load translations", error);
    }
  };

  const loadPerformanceData = async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.get(
        `/performance/${districtCode}?limit=12`
      );
      const data = response.data;
      setPerformances(data);
      if (data.length > 0) {
        setCurrentPerformance(data[0]);
        if (data.length > 1) {
          setPreviousPerformance(data[1]);
        }
      }
    } catch (error) {
      console.error("Failed to load performance data", error);
      toast.error(
        translations.no_data || "Failed to load performance data"
      );
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 10000000) return `${(num / 10000000).toFixed(2)} Cr`;
    if (num >= 100000) return `${(num / 100000).toFixed(2)} L`;
    if (num >= 1000) return `${(num / 1000).toFixed(2)} K`;
    return num.toLocaleString();
  };

  const formatCurrency = (num) => {
    return `₹${formatNumber(num)}`;
  };

  const getPercentageChange = (current, previous) => {
    if (!previous || previous === 0) return 0;
    return (((current - previous) / previous) * 100).toFixed(1);
  };

  const getMonthName = (month, lang) => {
    const months = {
      en: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ],
      hi: [
        "जन",
        "फर",
        "मार्च",
        "अप्रैल",
        "मई",
        "जून",
        "जुल",
        "अग",
        "सित",
        "अक्टू",
        "नव",
        "दिस",
      ],
    };
    return months[lang] ? months[lang][month - 1] : months.en[month - 1];
  };

  const StatCard = ({ icon: Icon, title, value, change, color, testId }) => {
    const isPositive = change >= 0;
    return (
      <Card
        className={`stat-card border-${color}-200 bg-gradient-to-br from-white to-${color}-50 shadow-md hover:shadow-xl`}
        data-testid={testId}
      >
        <CardContent className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div
              className={`w-14 h-14 bg-${color}-100 rounded-2xl flex items-center justify-center`}
            >
              <Icon className={`w-7 h-7 text-${color}-600`} />
            </div>
            {change !== null && (
              <div
                className={`flex items-center space-x-1 text-sm font-semibold ${
                  isPositive ? "text-green-600" : "text-red-600"
                }`}
              >
                {isPositive ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                <span>{Math.abs(change)}%</span>
              </div>
            )}
          </div>
          <h3 className="text-sm text-gray-600 mb-2">{title}</h3>
          <p className="text-2xl sm:text-3xl font-bold text-gray-900">
            {value}
          </p>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-pulse">
            <div className="w-16 h-16 bg-emerald-500 rounded-full mx-auto mb-4"></div>
            <p className="text-emerald-700 text-lg">
              {language === "hi" ? "लोड हो रहा है..." : "Loading..."}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!currentPerformance) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-emerald-700 text-lg mb-4">
            {translations.no_data || "No data available"}
          </p>
          <Button
            onClick={() => navigate("/")}
            className="bg-emerald-500 hover:bg-emerald-600"
          >
            {language === "hi" ? "वापस जाएं" : "Go Back"}
          </Button>
        </div>
      </div>
    );
  }

  const budgetUtilization = (
    (currentPerformance.total_expenditure /
      currentPerformance.total_budget_allocated) *
    100
  ).toFixed(1);

  const worksCompletionRate = (
    (currentPerformance.completed_works / currentPerformance.total_works) *
    100
  ).toFixed(1);

  const womenParticipationRate = (
    (currentPerformance.women_person_days /
      currentPerformance.person_days_generated) *
    100
  ).toFixed(1);

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-emerald-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center space-x-3">
              <Button
                onClick={() => navigate("/")}
                variant="outline"
                size="icon"
                className="border-emerald-200 hover:bg-emerald-50"
                data-testid="back-btn"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-emerald-900">
                  {language === "hi"
                    ? currentPerformance.district_name
                    : currentPerformance.district_name}
                </h1>
                <p className="text-sm text-emerald-600">
                  {currentPerformance.state_name} •{" "}
                  {getMonthName(currentPerformance.month, language)}{" "}
                  {currentPerformance.year}
                </p>
              </div>
            </div>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger
                className="w-32 bg-white border-emerald-200"
                data-testid="language-selector-dashboard"
              >
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="hi">हिंदी</SelectItem>
                <SelectItem value="ta">தமிழ்</SelectItem>
                <SelectItem value="te">తెలుగు</SelectItem>
                <SelectItem value="bn">বাংলা</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Users}
            title={translations.active_workers || "Active Workers"}
            value={formatNumber(currentPerformance.active_workers)}
            change={
              previousPerformance
                ? getPercentageChange(
                    currentPerformance.active_workers,
                    previousPerformance.active_workers
                  )
                : null
            }
            color="emerald"
            testId="active-workers-card"
          />

          <StatCard
            icon={Calendar}
            title={translations.person_days || "Person Days"}
            value={formatNumber(currentPerformance.person_days_generated)}
            change={
              previousPerformance
                ? getPercentageChange(
                    currentPerformance.person_days_generated,
                    previousPerformance.person_days_generated
                  )
                : null
            }
            color="teal"
            testId="person-days-card"
          />

          <StatCard
            icon={Wallet}
            title={translations.avg_wage || "Avg Daily Wage"}
            value={formatCurrency(currentPerformance.average_wage_per_day)}
            change={
              previousPerformance
                ? getPercentageChange(
                    currentPerformance.average_wage_per_day,
                    previousPerformance.average_wage_per_day
                  )
                : null
            }
            color="cyan"
            testId="avg-wage-card"
          />

          <StatCard
            icon={Briefcase}
            title={translations.works_completed || "Works Completed"}
            value={currentPerformance.completed_works}
            change={
              previousPerformance
                ? getPercentageChange(
                    currentPerformance.completed_works,
                    previousPerformance.completed_works
                  )
                : null
            }
            color="indigo"
            testId="works-completed-card"
          />
        </div>

        {/* Progress Bars */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="border-emerald-200 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-base text-emerald-800">
                {translations.budget_utilization || "Budget Utilization"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-3xl font-bold text-emerald-900">
                    {budgetUtilization}%
                  </span>
                  <span
                    className={`text-sm font-semibold ${
                      budgetUtilization >= 80
                        ? "text-green-600"
                        : budgetUtilization >= 60
                        ? "text-yellow-600"
                        : "text-red-600"
                    }`}
                  >
                    {budgetUtilization >= 80
                      ? language === "hi"
                        ? "अच्छा"
                        : "Good"
                      : budgetUtilization >= 60
                      ? language === "hi"
                        ? "ठीक"
                        : "Fair"
                      : language === "hi"
                      ? "सुधार चाहिए"
                      : "Needs Improvement"}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${
                      budgetUtilization >= 80
                        ? "bg-green-500"
                        : budgetUtilization >= 60
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                    style={{ width: `${budgetUtilization}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-600">
                  {formatCurrency(currentPerformance.total_expenditure)} /{" "}
                  {formatCurrency(currentPerformance.total_budget_allocated)}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-teal-200 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-base text-teal-800">
                {translations.works_completed || "Works Completion"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-3xl font-bold text-teal-900">
                    {worksCompletionRate}%
                  </span>
                  <span
                    className={`text-sm font-semibold ${
                      worksCompletionRate >= 75
                        ? "text-green-600"
                        : worksCompletionRate >= 50
                        ? "text-yellow-600"
                        : "text-red-600"
                    }`}
                  >
                    {worksCompletionRate >= 75
                      ? language === "hi"
                        ? "अच्छा"
                        : "Good"
                      : worksCompletionRate >= 50
                      ? language === "hi"
                        ? "ठीक"
                        : "Fair"
                      : language === "hi"
                      ? "सुधार चाहिए"
                      : "Needs Improvement"}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${
                      worksCompletionRate >= 75
                        ? "bg-green-500"
                        : worksCompletionRate >= 50
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                    style={{ width: `${worksCompletionRate}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-600">
                  {currentPerformance.completed_works} /{" "}
                  {currentPerformance.total_works}{" "}
                  {language === "hi" ? "कार्य" : "works"}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-pink-200 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-base text-pink-800">
                {translations.women_participation || "Women's Participation"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-3xl font-bold text-pink-900">
                    {womenParticipationRate}%
                  </span>
                  <span
                    className={`text-sm font-semibold ${
                      womenParticipationRate >= 45
                        ? "text-green-600"
                        : womenParticipationRate >= 33
                        ? "text-yellow-600"
                        : "text-red-600"
                    }`}
                  >
                    {womenParticipationRate >= 45
                      ? language === "hi"
                        ? "अच्छा"
                        : "Good"
                      : womenParticipationRate >= 33
                      ? language === "hi"
                        ? "ठीक"
                        : "Fair"
                      : language === "hi"
                      ? "सुधार चाहिए"
                      : "Needs Improvement"}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${
                      womenParticipationRate >= 45
                        ? "bg-green-500"
                        : womenParticipationRate >= 33
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                    style={{ width: `${womenParticipationRate}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-600">
                  {formatNumber(currentPerformance.women_person_days)}{" "}
                  {language === "hi" ? "दिन" : "days"}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Info - Expandable */}
        <Card className="border-emerald-200 bg-white/80 backdrop-blur-sm mb-8">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-xl text-emerald-900">
                {language === "hi" ? "विस्तृत जानकारी" : "Detailed Information"}
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                className="text-emerald-700"
                data-testid="toggle-details-btn"
              >
                {showDetails ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </Button>
            </div>
          </CardHeader>
          {showDetails && (
            <CardContent className="fade-in">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-semibold text-emerald-800 text-lg">
                    {language === "hi" ? "रोजगार विवरण" : "Employment Details"}
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">
                        {language === "hi" ? "कुल जॉब कार्ड" : "Total Job Cards"}
                      </span>
                      <span className="font-semibold">
                        {formatNumber(currentPerformance.total_job_cards)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">
                        {language === "hi"
                          ? "सक्रिय जॉब कार्ड"
                          : "Active Job Cards"}
                      </span>
                      <span className="font-semibold">
                        {formatNumber(currentPerformance.active_job_cards)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">
                        {language === "hi" ? "कुल कामगार" : "Total Workers"}
                      </span>
                      <span className="font-semibold">
                        {formatNumber(currentPerformance.total_workers)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">
                        {language === "hi"
                          ? "घर के औसत दिन"
                          : "Avg Days/Household"}
                      </span>
                      <span className="font-semibold">
                        {currentPerformance.average_days_per_household} days
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-semibold text-emerald-800 text-lg">
                    {language === "hi" ? "वित्तीय विवरण" : "Financial Details"}
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">
                        {language === "hi" ? "मजदूरी खर्च" : "Wage Expenditure"}
                      </span>
                      <span className="font-semibold">
                        {formatCurrency(currentPerformance.wage_expenditure)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">
                        {language === "hi"
                          ? "सामग्री खर्च"
                          : "Material Expenditure"}
                      </span>
                      <span className="font-semibold">
                        {formatCurrency(currentPerformance.material_expenditure)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">
                        {language === "hi" ? "चल रहे कार्य" : "Ongoing Works"}
                      </span>
                      <span className="font-semibold">
                        {currentPerformance.ongoing_works}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">
                        {language === "hi"
                          ? "SC व्यक्ति-दिवस"
                          : "SC Person Days"}
                      </span>
                      <span className="font-semibold">
                        {formatNumber(currentPerformance.sc_person_days)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          )}
        </Card>

        {/* Historical Trend */}
        <Card className="border-emerald-200 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl text-emerald-900">
              {language === "hi"
                ? "पिछले 6 महीनों का प्रदर्शन"
                : "Last 6 Months Performance"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {performances.slice(0, 6).map((perf, index) => (
                <div
                  key={perf.id}
                  className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-emerald-50 to-teal-50 hover:shadow-md transition-shadow"
                  data-testid={`historical-month-${index}`}
                >
                  <div className="flex-1">
                    <p className="font-semibold text-emerald-900">
                      {getMonthName(perf.month, language)} {perf.year}
                    </p>
                    <p className="text-sm text-emerald-600">
                      {formatNumber(perf.active_workers)}{" "}
                      {language === "hi" ? "कामगार" : "workers"} •{" "}
                      {formatNumber(perf.person_days_generated)}{" "}
                      {language === "hi" ? "दिन" : "days"}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">
                      {language === "hi" ? "बजट" : "Budget"}
                    </p>
                    <p className="font-semibold text-emerald-900">
                      {(
                        (perf.total_expenditure / perf.total_budget_allocated) *
                        100
                      ).toFixed(0)}
                      %
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default DashboardPage;
