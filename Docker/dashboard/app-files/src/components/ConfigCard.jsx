import React, { useEffect } from 'react';
import Slider from '@mui/material/Slider';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';

import "../style/card-style.css";
import "../style/config-card-style.css";

export const ConfigCard = (props) => {
    const SIMULATION_MODE = 0;
    const CAN_MODE = 1;

    const [value, setValue] = React.useState(props.value);
    const [mode, setMode] = React.useState(props.mode)

    useEffect(() => setValue(props.value), [props.value]);
    useEffect(() => setMode(props.mode), [props.mode]);

    const selectionChanged = (event) => {
        const value = event.target.value;
        console.log(value);
        
        let config = props.config;
        config.mode = (value == CAN_MODE ? "CAN" : "SIMULATION");
        props.setConfig(config);

        setMode(config.mode);
    };

    const sliderChanged = (event) => {
        const value = event.target.value;
        console.log(value);
        
        let config = props.config;
        props.title == "Fuel" ? config.level_limit = value : config.interval = value;
        props.setConfig(config);

        setValue(value);
    }

    return (
        <div className="card">
            <div className="title">{props.title}</div>
            <br></br>
            <div className="config-option">
                <div className="subtitle">{props.title == "Fuel" ? "Limit" : "Interval" }</div>
                <Slider 
                    min={Number(props.min)} 
                    max={Number(props.max)} 
                    value={value}
                    aria-label="Default" 
                    valueLabelDisplay="auto"
                    onChange={sliderChanged}
                />
            </div>
            <br></br>
            <div className="config-option">
                <div className="subtitle">Mode</div>
                <Select
                    value={mode == "CAN" ? 1 : 0}
                    onLoadStart={() => setMode(props.mode)}
                    onChange={selectionChanged}
                >
                    <MenuItem value={SIMULATION_MODE}>Simulation</MenuItem>
                    {props.mode == "CAN" ? <MenuItem value={CAN_MODE}>Device</MenuItem> : null}
                </Select>
            </div>
        </div>
    );
};

export default ConfigCard;