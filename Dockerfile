FROM mambaorg/micromamba:1.5.10

# Create an env with everything needed for your workflow
RUN micromamba create -y -n spear-qc -c conda-forge \
    python=3.11 \
    cylc-flow \
    netcdf4 numpy pyyaml \
    matplotlib cartopy \
    && micromamba clean -a -y

# Make the env active by default
ENV PATH=/opt/conda/envs/spear-qc/bin:$PATH
ENV CONDA_DEFAULT_ENV=spear-qc

# Headless plotting + stable threading defaults
ENV MPLBACKEND=Agg
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Cylc will store runs here (we will mount a host dir to this)
ENV CYLC_RUN_DIR=/cylc-run
ENV HOME=/home/cylc

# Non-root user (matches common UID 1000; adjust if needed)
USER root
RUN useradd -m -u 1000 cylc && mkdir -p /src /data /cylc-run \
    && chown -R cylc:cylc /src /data /cylc-run /home/cylc
USER cylc

WORKDIR /src

CMD ["/bin/bash"]
