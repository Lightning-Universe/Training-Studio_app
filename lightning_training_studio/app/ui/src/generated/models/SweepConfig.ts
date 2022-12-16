/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Distributions } from './Distributions';
import type { ExperimentConfig } from './ExperimentConfig';

export type SweepConfig = {
    sweep_id: string;
    script_path: string;
    total_experiments: number;
    parallel_experiments: number;
    total_experiments_done?: number;
    requirements: Array<string>;
    packages: Array<string>;
    script_args: Array<string>;
    algorithm: string;
    distributions: Record<string, Distributions>;
    logger_url?: string;
    experiments: Record<string, ExperimentConfig>;
    framework: string;
    cloud_compute?: string;
    num_nodes?: number;
    artifacts_path?: string;
    logger: string;
    direction: string;
    stage?: string;
    desired_stage?: string;
    shm_size?: number;
    disk_size?: number;
    pip_install_source?: boolean;
    data: Record<string, string>;
    username?: string;
};
