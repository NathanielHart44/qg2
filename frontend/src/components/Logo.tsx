import { Box as MUIBox, Stack, Typography } from "@mui/material";
import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { MetadataContext } from "src/contexts/MetadataContext";
import useAuth from "src/hooks/useAuth";
import { PATH_PAGE } from "src/routes/paths";

// ----------------------------------------------------------------------

export default function Logo() {

    const { isAuthenticated } = useAuth();
    const { currentUser } = useContext(MetadataContext);
    const navigate = useNavigate();

    let path = PATH_PAGE.home;
    if (!isAuthenticated || !currentUser) { path = PATH_PAGE.landing };

    return (
        <Stack direction={'row'} alignItems={'center'} onClick={() => { navigate(path) }} sx={{ cursor: 'pointer' }}>
            <MUIBox component={'div'} sx={{ maxHeight: '100%', maxWidth: '60px' }}>
                <img src="/icons/qlogo.png" alt="QGame Logo" loading="lazy" />
            </MUIBox>
            <Typography variant="h6" component="div" fontFamily={"Mystery Quest"} sx={{ flexGrow: 1, whiteSpace: 'nowrap' }}>
                QGame
            </Typography>
        </Stack>
    )
}