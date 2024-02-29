import { Divider, Grid, Stack, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import Page from "src/components/base/Page";
import { PATH_PAGE } from "src/routes/paths";
import { useContext, useEffect, useState } from "react";
import { MetadataContext } from "src/contexts/MetadataContext";
import { AppInstallContext } from "src/contexts/AppInstallContext";
import { useApiCall } from "src/hooks/useApiCall";
import { useSnackbar } from "notistack";
import NavButton from "src/components/base/NavButton";
import { MAIN_API } from "src/config";
import ContactPop from "src/components/ContactPop";

// ----------------------------------------------------------------------

export default function Home() {

    const navigate = useNavigate();
    const { isIOS, isPWA } = useContext(MetadataContext);
    const { installPrompt } = useContext(AppInstallContext);
    const { apiCall } = useApiCall();
    const { enqueueSnackbar } = useSnackbar();

    const [awaitingResponse, setAwaitingResponse] = useState<boolean>(false);
    const [appInstalled, setAppInstalled] = useState<boolean>(false);
    const [feedbackOpen, setFeedbackOpen] = useState<boolean>(false);

    const handleFeedback = () => { setFeedbackOpen(!feedbackOpen) };

    const handleInstallClick = () => {
        if (installPrompt) {
            installPrompt.prompt(); // Show the install prompt
            installPrompt.userChoice.then((choiceResult: any) => {
                if (choiceResult.outcome === 'accepted') {
                localStorage.setItem('appInstalled', 'true');
                setAppInstalled(true);
                } else {
                // console.log('User dismissed the install prompt');
                }
            });
        } else {
            console.log('No install prompt found');
        }
    };

    useEffect(() => {
        if (localStorage.getItem('appInstalled') === 'true') {
            setAppInstalled(true);
        }
    }, []);

    return (
        <Page title="Home">
            <Stack spacing={6} width={'100%'} justifyContent={'center'} alignItems={'center'}>

                {/* <HomeNotices /> */}
                <Typography variant={'h3'}>Welcome to QGame!</Typography>
                <Divider sx={{ width: '65%' }} />

                <Grid container gap={2} width={'100%'} justifyContent={'center'} alignItems={'center'}>
                    {/* <Grid item xs={8} sm={6} md={4} lg={3} xl={3}>
                        <NavButton
                            title={'New Game'}
                            text={'Play a game in either "Classic" or "With List" mode.'}
                            image={`${MAIN_API.asset_url_base}additional-assets/example_6.png`}
                            onClick={() => { navigate(PATH_PAGE.game_start_router) }}
                            isDisabled={awaitingResponse}
                        />
                    </Grid> */}
                </Grid>
                
                <Divider sx={{ width: '65%' }} />

                <Grid container gap={2} width={'100%'} justifyContent={'center'} alignItems={'center'}>
                    {(!isPWA && !appInstalled) &&
                        <Grid item xs={8} sm={6} md={4} lg={3} xl={3}>
                            <NavButton
                                title={'Install App'}
                                text={
                                    isIOS ?
                                    'Want to install the app? Just tap the share button, then "Add to Home Screen".' :
                                    'Install the app to your device for a better experience.'
                                }
                                image={`${MAIN_API.asset_url_base}additional-assets/example_14.png`}
                                onClick={isIOS ? () => { } : handleInstallClick}
                                isDisabled={awaitingResponse || (isIOS && !isPWA) || !installPrompt}
                            />
                        </Grid>
                    }
                    {(isPWA || appInstalled) &&
                        <Grid item xs={8} sm={6} md={4} lg={3} xl={3}>
                            <NavButton
                                title={'App Installed'}
                                text={'The app has been installed.'}
                                image={`${MAIN_API.asset_url_base}additional-assets/example_14.png`}
                                onClick={() => { }}
                                isDisabled={awaitingResponse || appInstalled || isPWA}
                            />
                        </Grid>
                    }
                    <Grid item xs={8} sm={6} md={4} lg={3} xl={3}>
                        <NavButton
                            title={'Feedback'}
                            text={'Have any feedback or bug reports? Let us know!'}
                            onClick={handleFeedback}
                            isDisabled={awaitingResponse}
                        />
                    </Grid>
                </Grid>
                <ContactPop
                    popOpen={feedbackOpen}
                    setPopOpen={setFeedbackOpen}
                />
            </Stack>
        </Page>
    );
};