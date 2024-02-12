import React, { useEffect } from "react";
import axios from "axios";
import ConfigCard from "../components/ConfigCard";
import Button from "@mui/material/Button";
import { useNavigate } from "react-router-dom";
import "../style/config-page.css";
import conf from "../conf.json";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

const Alert = React.forwardRef(function Alert(props, ref) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export const ConfigPage = () => {
    const navigate = useNavigate();
    
    const [tempConfig, setTempConfig] = React.useState({});
    const [loadConfig, setLoadConfig] = React.useState({});
    const [fuelConfig, setFuelConfig] = React.useState({});
    const [snackbar, setSnackbar] = React.useState(false);

    let gatewayApiUrl = conf.IOTDEVICE1_GATEWAY_API_URL;

    const getGatewayApiUrl = (username) => {
        const regex = new RegExp(`${username}_GATEWAY_API_URL`);
        Object.keys(conf).forEach(key => {
            if(key.match(regex)){
                return conf[key];
            }
        });

        return conf.IOTDEVICE1_GATEWAY_API_URL;
    };

    useEffect(() => {
        if (
          !sessionStorage.getItem("jwt") ||
          sessionStorage.getItem("jwt") === "" ||
          !sessionStorage.getItem("device") ||
          sessionStorage.getItem("device") === ""
        )
        navigate("/iot-platform/login");

        axios
        .get(conf.server_url + `/auth/jwt-check`, {
            headers: {
            Authorization: "Bearer " + sessionStorage.getItem("jwt"),
            },
        })
        .then((res) => {
            console.log("JWT OK");
        })
        .catch((exc) => {
            console.log("ERROR::JWT_NOT_VALID");
            navigate("/iot-platform/login");
        });

        gatewayApiUrl = getGatewayApiUrl(sessionStorage.getItem("device"));

        // Request current configuration
        axios
        .get(gatewayApiUrl, {
            headers: {},
        })
        .then((res) => {
            console.log("Initial data:");
            console.log(res.data);

            setTempConfig(res.data.temp_settings);
            setLoadConfig(res.data.load_settings);
            setFuelConfig(res.data.fuel_settings);
        })
        .catch((exc) => {
            console.log("ERROR::GATEWAY_API::INITIAL_GET");
            console.log(exc);
            setSnackbar(true);
        });
    }, []);

    const allPropertiesSet = () => {
        return Object.hasOwn(tempConfig, 'interval')    &&
               Object.hasOwn(tempConfig, 'mode')        &&
               Object.hasOwn(loadConfig, 'interval')    &&
               Object.hasOwn(loadConfig, 'mode')        &&
               Object.hasOwn(fuelConfig, 'level_limit') &&
               Object.hasOwn(fuelConfig, 'mode');
    };
    
    const submitConfig = () => {
        console.log("Configuration submitted.");
        console.log(tempConfig);
        console.log(loadConfig);
        console.log(fuelConfig);

        if(!allPropertiesSet()){
            console.log("ERROR: Not all properties are set.");
            setSnackbar(true);
            return;
        }

        axios.post(
            gatewayApiUrl,
            {
                "temp_settings" : {
                    "interval": tempConfig.interval,
                    "mode": tempConfig.mode
                },
                "load_settings" : {
                    "interval": loadConfig.interval,
                    "mode": loadConfig.mode
                },
                "fuel_settings" : {
                    "level_limit": fuelConfig.level_limit,
                    "mode": fuelConfig.mode
                }
            }
        ).then((res) => {
            console.log("Configuration accepted");
            navigate("/iot-platform/dashboard");
        }).catch((exc) => {
            console.log("ERROR::GATEWAY_API::POST");
            console.log(exc);
            setSnackbar(true);
        });
    };

    const handleCloseSnackbar = (event, reason) => {
        if (reason === "clickaway") {
          return;
        }
    
        setSnackbar(false);
    };

    return (
      <div>
        <Snackbar
            open={snackbar}
            autoHideDuration={4000}
            onClose={handleCloseSnackbar}
        >
            <Alert
                onClose={handleCloseSnackbar}
                severity="error"
                sx={{ width: "100%" }}
                >
                Gateway configuration endpoint can't be reached.
            </Alert>
        </Snackbar>
        <div className="buttons">
            <Button
                variant="outlined"
                color="primary"
                className=""
                onClick={() => navigate('/iot-platform/dashboard')}
            >
                Dashboard
            </Button>
            <Button
                variant="outlined"
                color="primary"
                className=""
                onClick={submitConfig}
            >
                Submit
            </Button>
        </div>
        
        <div class="config-options">
            <ConfigCard
                title="Temperature"
                value={tempConfig.interval || ''}
                min={conf.TEMP_MIN}
                max={conf.TEMP_MAX}
                mode={tempConfig.mode || ''}
                config={tempConfig}
                setConfig={setTempConfig}
                marks
            ></ConfigCard>
            <ConfigCard
                title="Load"
                value={loadConfig.interval || ''}
                min={conf.LOAD_MIN}
                max={conf.LOAD_MAX}
                mode={loadConfig.mode || ''}
                config={loadConfig}
                setConfig={setLoadConfig}
                marks
            ></ConfigCard>
            <ConfigCard
                title="Fuel"
                value={fuelConfig.level_limit || ''}
                min={conf.FUEL_MIN}
                max={conf.FUEL_MAX}
                mode={fuelConfig.mode || ''}
                config={fuelConfig}
                setConfig={setFuelConfig}
                marks
            ></ConfigCard>
        </div>
      </div>
    );
};

export default ConfigPage;
