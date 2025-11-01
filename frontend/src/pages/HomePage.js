import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { axiosInstance } from "../App";
import { Button } from "../components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Card, CardContent } from "../components/ui/card";
import { MapPin, Users, TrendingUp, ChevronRight } from "lucide-react";
import { toast } from "sonner";

const HomePage = () => {
  const navigate = useNavigate();
  const [language, setLanguage] = useState("en");
  const [translations, setTranslations] = useState({});
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [selectedState, setSelectedState] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTranslations();
    loadStates();
  }, [language]);

  const loadTranslations = async () => {
    try {
      const response = await axiosInstance.get(`/translations/${language}`);
      setTranslations(response.data);
    } catch (error) {
      console.error("Failed to load translations", error);
    }
  };

  const loadStates = async () => {
    try {
      const response = await axiosInstance.get("/states");
      setStates(response.data);
    } catch (error) {
      console.error("Failed to load states", error);
      toast.error("Failed to load states");
    }
  };

  const loadDistricts = async (stateCode) => {
    setLoading(true);
    try {
      const response = await axiosInstance.get(`/districts/${stateCode}`);
      setDistricts(response.data);
    } catch (error) {
      console.error("Failed to load districts", error);
      toast.error("Failed to load districts");
    } finally {
      setLoading(false);
    }
  };

  const handleStateChange = (value) => {
    setSelectedState(value);
    setSelectedDistrict("");
    setDistricts([]);
    loadDistricts(value);
  };

  const handleViewDashboard = () => {
    if (!selectedDistrict) {
      toast.error(translations.select_district || "Please select a district");
      return;
    }
    navigate(`/dashboard/${selectedDistrict}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-emerald-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
                <Users className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-emerald-900">
                  {translations.app_title || "MGNREGA Dashboard"}
                </h1>
                <p className="text-sm text-emerald-600 hidden sm:block">
                  {language === "hi"
                    ? "अपने जिले का प्रदर्शन देखें"
                    : "Track Your District Performance"}
                </p>
              </div>
            </div>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger
                className="w-32 bg-white border-emerald-200"
                data-testid="language-selector"
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

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-emerald-900 mb-4">
            {language === "hi"
              ? "हमारी आवाज़, हमारे अधिकार"
              : "Our Voice, Our Rights"}
          </h2>
          <p className="text-lg sm:text-xl text-emerald-700 max-w-3xl mx-auto">
            {language === "hi"
              ? "अपने जिले में मनरेगा कार्यक्रम का प्रदर्शन देखें और समझें"
              : "View and understand MGNREGA program performance in your district"}
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Card className="border-emerald-200 bg-white/60 backdrop-blur-sm hover:shadow-lg transition-shadow">
            <CardContent className="p-6 text-center">
              <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <MapPin className="w-8 h-8 text-emerald-600" />
              </div>
              <h3 className="text-xl font-semibold text-emerald-900 mb-2">
                {language === "hi" ? "अपना जिला चुनें" : "Select District"}
              </h3>
              <p className="text-emerald-600">
                {language === "hi"
                  ? "आसानी से अपना राज्य और जिला खोजें"
                  : "Easy access to your state and district"}
              </p>
            </CardContent>
          </Card>

          <Card className="border-teal-200 bg-white/60 backdrop-blur-sm hover:shadow-lg transition-shadow">
            <CardContent className="p-6 text-center">
              <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-teal-600" />
              </div>
              <h3 className="text-xl font-semibold text-teal-900 mb-2">
                {language === "hi" ? "प्रदर्शन देखें" : "View Performance"}
              </h3>
              <p className="text-teal-600">
                {language === "hi"
                  ? "सरल चार्ट और संख्याएं"
                  : "Simple charts and numbers"}
              </p>
            </CardContent>
          </Card>

          <Card className="border-cyan-200 bg-white/60 backdrop-blur-sm hover:shadow-lg transition-shadow">
            <CardContent className="p-6 text-center">
              <div className="w-16 h-16 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-cyan-600" />
              </div>
              <h3 className="text-xl font-semibold text-cyan-900 mb-2">
                {language === "hi" ? "समझें" : "Understand"}
              </h3>
              <p className="text-cyan-600">
                {language === "hi"
                  ? "आसान भाषा में जानकारी"
                  : "Information in simple language"}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Selection Card */}
        <Card className="max-w-2xl mx-auto border-emerald-200 bg-white/80 backdrop-blur-md shadow-xl">
          <CardContent className="p-8">
            <h3 className="text-2xl sm:text-3xl font-bold text-emerald-900 mb-6 text-center">
              {language === "hi"
                ? "अपना जिला चुनें"
                : "Choose Your District"}
            </h3>

            <div className="space-y-6">
              {/* State Selection */}
              <div>
                <label className="block text-base sm:text-lg font-semibold text-emerald-800 mb-3">
                  {translations.select_state || "Select Your State"}
                </label>
                <Select
                  value={selectedState}
                  onValueChange={handleStateChange}
                >
                  <SelectTrigger
                    className="w-full h-14 text-base sm:text-lg border-2 border-emerald-200 hover:border-emerald-400"
                    data-testid="state-selector"
                  >
                    <SelectValue
                      placeholder={
                        language === "hi" ? "राज्य चुनें" : "Choose State"
                      }
                    />
                  </SelectTrigger>
                  <SelectContent>
                    {states.map((state) => (
                      <SelectItem
                        key={state.state_code}
                        value={state.state_code}
                        className="text-base sm:text-lg py-3"
                      >
                        {language === "hi"
                          ? state.state_name_hi
                          : state.state_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* District Selection */}
              {selectedState && (
                <div className="fade-in">
                  <label className="block text-base sm:text-lg font-semibold text-emerald-800 mb-3">
                    {translations.select_district || "Select Your District"}
                  </label>
                  <Select
                    value={selectedDistrict}
                    onValueChange={setSelectedDistrict}
                    disabled={loading || districts.length === 0}
                  >
                    <SelectTrigger
                      className="w-full h-14 text-base sm:text-lg border-2 border-emerald-200 hover:border-emerald-400"
                      data-testid="district-selector"
                    >
                      <SelectValue
                        placeholder={
                          loading
                            ? language === "hi"
                              ? "लोड हो रहा है..."
                              : "Loading..."
                            : language === "hi"
                            ? "जिला चुनें"
                            : "Choose District"
                        }
                      />
                    </SelectTrigger>
                    <SelectContent>
                      {districts.map((district) => (
                        <SelectItem
                          key={district.district_code}
                          value={district.district_code}
                          className="text-base sm:text-lg py-3"
                        >
                          {language === "hi"
                            ? district.district_name_hi
                            : district.district_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* View Dashboard Button */}
              <Button
                onClick={handleViewDashboard}
                disabled={!selectedDistrict}
                className="w-full h-14 text-lg sm:text-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-semibold rounded-xl shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="view-dashboard-btn"
              >
                {translations.view_details || "View Dashboard"}
                <ChevronRight className="ml-2 w-6 h-6" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Info Section */}
        <div className="mt-12 text-center">
          <p className="text-emerald-700 text-base sm:text-lg">
            {language === "hi"
              ? "12.15 करोड़ ग्रामीण भारतीयों ने 2025 में मनरेगा से लाभ उठाया"
              : "12.15 Crore rural Indians benefited from MGNREGA in 2025"}
          </p>
        </div>
      </main>
    </div>
  );
};

export default HomePage;
